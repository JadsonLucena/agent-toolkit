#!/usr/bin/env python3
"""Validate routing scenarios and score host-observed capability activations.

Catalog validation is structural. It does not invoke an LLM or claim runtime routing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = ("skill", "agent", "command", "rule")
MODES = ("implicit", "explicit", "contextual")
HOSTS = ("cursor", "codex", "gemini-cli", "claude-code")


def capability_inventory(root: Path) -> dict[str, set[str]]:
    inventory: dict[str, set[str]] = {kind: set() for kind in KINDS}
    paths = {
        "skill": root.glob("contexts/*/skills/*/SKILL.md"),
        "agent": root.glob("contexts/*/agents/*.md"),
        "command": root.glob("contexts/*/commands/*.md"),
        "rule": root.glob("contexts/*/rules/*.md"),
    }
    for kind, files in paths.items():
        for path in files:
            if kind == "rule":
                name = path.stem
            else:
                header = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
                match = re.search(r"(?m)^name: ([a-z][a-z0-9-]*)$", header)
                name = match.group(1) if match else ""
            if not name:
                raise ValueError(f"{path}: missing public name")
            if name in inventory[kind]:
                raise ValueError(f"{kind}: duplicate public identifier {name}")
            inventory[kind].add(name)
    return inventory


def validate_catalog(catalog: dict, inventory: dict[str, set[str]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        return ["catalog: expected schema_version=1 and a JSON object"]
    cases = catalog.get("cases")
    if not isinstance(cases, list) or not cases:
        return ["catalog: cases must be a nonempty array"]
    seen: set[str] = set()
    for i, case in enumerate(cases):
        label = f"cases[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected an object")
            continue
        identifier = case.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identifier):
            errors.append(f"{label}: invalid id")
        elif identifier in seen:
            errors.append(f"{label}: duplicate id {identifier}")
        else:
            seen.add(identifier)
        if case.get("kind") not in KINDS:
            errors.append(f"{label}: invalid capability kind")
            continue
        if case.get("mode") not in MODES:
            errors.append(f"{label}: invalid invocation mode")
        if not isinstance(case.get("prompt"), str) or len(case["prompt"].strip()) < 20:
            errors.append(f"{label}: prompt is missing or too short")
        expected = case.get("expected")
        forbidden = case.get("forbidden")
        if not isinstance(expected, list) or not isinstance(forbidden, list):
            errors.append(f"{label}: expected and forbidden must be arrays")
            continue
        if any(not isinstance(name, str) for name in expected + forbidden):
            errors.append(f"{label}: all capability names must be strings")
            continue
        if not expected and not forbidden:
            errors.append(f"{label}: require an expected or forbidden routing condition")
        for name_list, key in ((expected, "expected"), (forbidden, "forbidden")):
            if len(name_list) != len(set(map(str, name_list))):
                errors.append(f"{label}: duplicate {key} entries")
            for name in name_list:
                if not isinstance(name, str) or name not in inventory[case["kind"]]:
                    errors.append(f"{label}: unknown {case['kind']} {key} {name!r}")
        if set(expected) & set(forbidden):
            errors.append(f"{label}: expected and forbidden overlap")
        if case["kind"] == "command" and expected and case.get("mode") != "explicit":
            errors.append(f"{label}: Commands must use explicit invocation in this catalog")
    return errors


def score_observations(cases: list[dict], observations: dict) -> dict:
    if not isinstance(observations, dict) or observations.get("schema_version") != 1:
        raise ValueError("observations: expected schema_version=1")
    if observations.get("host") not in HOSTS:
        raise ValueError(f"observations: host must be one of {', '.join(HOSTS)}")
    if (not isinstance(observations.get("plugin_revision"), str)
            or not observations["plugin_revision"].strip()
            or observations["plugin_revision"] in {"not-installed", "ACTUAL_INSTALLED_SHA"}):
        raise ValueError("observations: record an actual installed plugin_revision")
    results = observations.get("results")
    if not isinstance(results, list):
        raise ValueError("observations: results must be an array")
    indexed: dict[str, dict] = {}
    valid_ids = {case["id"] for case in cases}
    for result in results:
        if not isinstance(result, dict):
            raise ValueError("observations: every result must be an object")
        identifier = result.get("id")
        if not isinstance(identifier, str):
            raise ValueError("observations: result missing id")
        if identifier in indexed:
            raise ValueError(f"observations: duplicate result {identifier}")
        indexed[identifier] = result
    # Superset results are permitted when scoring a single capability kind.

    total_tp = total_fp = total_fn = forbidden_activations = 0
    measured = unsupported = 0
    failures: list[dict] = []
    pending: list[str] = []
    for case in cases:
        identifier = case["id"]
        result = indexed.get(identifier)
        if result is None:
            pending.append(identifier)
            continue
        status = result.get("status")
        if status in {"unsupported", "not-run"}:
            if result.get("events") not in ([], None):
                raise ValueError(f"{identifier}: an unmeasured result cannot contain activation events")
            if status == "unsupported":
                unsupported += 1
            else:
                pending.append(identifier)
            continue
        if status != "observed":
            raise ValueError(f"{identifier}: status must be observed, not-run, or unsupported")
        events = result.get("events")
        if not isinstance(events, list):
            raise ValueError(f"{identifier}: observed status requires an events array")
        selected: set[str] = set()
        for event in events:
            if not isinstance(event, dict):
                raise ValueError(f"{identifier}: invalid event")
            if (event.get("origin") != "host" or event.get("action") != "activated"
                    or event.get("kind") not in KINDS or not isinstance(event.get("name"), str)
                    or not isinstance(event.get("evidence_ref"), str) or not event["evidence_ref"].strip()):
                raise ValueError(f"{identifier}: activation requires a host event and nonempty evidence_ref; model claims are not evidence")
            if event["kind"] == case["kind"]:
                selected.add(event["name"])
        measured += 1
        expected = set(case["expected"])
        forbidden = set(case["forbidden"])
        tp = len(selected & expected)
        fp = len(selected - expected)
        fn = len(expected - selected)
        forbidden_hits = selected & forbidden
        total_tp += tp
        total_fp += fp
        total_fn += fn
        forbidden_activations += len(forbidden_hits)
        if fp or fn or forbidden_hits:
            failures.append({
                "id": identifier,
                "missing": sorted(expected - selected),
                "unexpected": sorted(selected - expected),
                "forbidden": sorted(forbidden_hits),
            })
    precision = (total_tp / (total_tp + total_fp) if total_tp + total_fp else None)
    recall = (total_tp / (total_tp + total_fn) if total_tp + total_fn else None)
    return {
        "status": ("FAIL" if failures else "INCOMPLETE" if pending or unsupported else "PASS"),
        "host": observations["host"],
        "plugin_revision": observations["plugin_revision"],
        "total_cases": len(cases),
        "measured_cases": measured,
        "not_run_cases": len(pending),
        "unsupported_cases": unsupported,
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
        "forbidden_activations": forbidden_activations,
        "precision": precision,
        "recall": recall,
        "failures": failures,
        "pending_ids": pending,
    }


def make_template(cases: list[dict], host: str, plugin_revision: str) -> dict:
    return {
        "schema_version": 1,
        "host": host,
        "plugin_revision": plugin_revision,
        "results": [
            {"id": case["id"], "status": "not-run", "events": []}
            for case in cases
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="evals/routing/cases.json")
    parser.add_argument("--observations", help="JSON host events; without it, only structural validation runs")
    parser.add_argument("--kind", choices=KINDS, help="score one capability kind")
    parser.add_argument("--template-host", choices=HOSTS, help="print a not-run observation template; does not execute a host")
    parser.add_argument("--plugin-revision", default="not-installed", help="record the actual installed SHA for a template")
    args = parser.parse_args(argv)
    try:
        catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
        errors = validate_catalog(catalog, capability_inventory(ROOT))
        if errors:
            for error in errors:
                print(f"INVALID: {error}", file=sys.stderr)
            return 2
        cases = [case for case in catalog["cases"] if not args.kind or case["kind"] == args.kind]
        if args.template_host:
            print(json.dumps(make_template(cases, args.template_host, args.plugin_revision), indent=2))
            return 0
        if not args.observations:
            print(f"STRUCTURAL_PASS; NOT_MEASURED: {len(cases)} routing scenarios validated; no host activation evidence supplied")
            return 0
        observations = json.loads(Path(args.observations).read_text(encoding="utf-8"))
        report = score_observations(cases, observations)
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
