#!/usr/bin/env python3
"""Evidence-backed, provider-neutral rubric runner for Requirements agent evaluations.

This validates reviewer observations; it does NOT run an LLM or judge semantics
automatically. PASSED means that a named evaluator recorded auditable evidence,
not that an independent automated behavior test executed.
"""
import argparse
import json
from pathlib import Path


VALID_RESULTS = {"pass", "fail", "uncertain"}
VALID_MODES = {"presence", "absence"}


def load_catalog(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("catalog requires version=1 and nonempty cases")
    seen = set()
    for case in data["cases"]:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError(f"missing or duplicate case id: {cid!r}")
        seen.add(cid)
        for field in ("command", "scenario", "input"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"{cid}: {field} must be nonempty")
        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{cid}: checks must be nonempty")
        check_ids = set()
        for check in checks:
            key = check.get("id")
            if not isinstance(key, str) or not key or key in check_ids:
                raise ValueError(f"{cid}: missing or duplicate check id {key!r}")
            check_ids.add(key)
            if check.get("mode") not in VALID_MODES:
                raise ValueError(f"{cid}/{key}: invalid mode")
            if not isinstance(check.get("criterion"), str) or not check["criterion"].strip():
                raise ValueError(f"{cid}/{key}: criterion must be nonempty")
    return data


def _transcript(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("assessment needs transcript path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("transcript must be a relative path without ..")
    base = root.resolve()
    target = (base / candidate).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError(f"transcript outside assessment directory or missing: {relative}")
    return target.read_text(encoding="utf-8")


def evaluate(catalog, observations, base_dir):
    if observations.get("version") != 1 or not isinstance(observations.get("assessments"), list):
        raise ValueError("observations require version=1 and assessments array")
    cases = {case["id"]: case for case in catalog["cases"]}
    assessments = {}
    for entry in observations["assessments"]:
        cid = entry.get("case_id")
        if cid not in cases or cid in assessments:
            raise ValueError(f"unknown or duplicate assessment: {cid!r}")
        assessments[cid] = entry

    summary = {"status": "PASSED", "cases_total": len(cases),
               "passed": 0, "failed": 0, "incomplete": 0, "details": []}
    for cid, case in cases.items():
        entry = assessments.get(cid)
        if entry is None:
            summary["incomplete"] += 1
            summary["details"].append({"case_id": cid, "status": "INCOMPLETE",
                                       "reason": "not assessed"})
            continue
        if not isinstance(entry.get("reviewer"), str) or not entry["reviewer"].strip():
            raise ValueError(f"{cid}: named reviewer required")
        text = _transcript(Path(base_dir), entry.get("transcript"))
        checks = entry.get("checks")
        if not isinstance(checks, list):
            raise ValueError(f"{cid}: checks must be an array")
        by_id = {}
        valid_ids = {c["id"] for c in case["checks"]}
        for check in checks:
            key = check.get("id")
            if key not in valid_ids or key in by_id:
                raise ValueError(f"{cid}: unknown or duplicate observation {key!r}")
            verdict = check.get("verdict")
            if verdict not in VALID_RESULTS:
                raise ValueError(f"{cid}/{key}: invalid verdict {verdict!r}")
            if verdict != "uncertain" and not str(check.get("rationale", "")).strip():
                raise ValueError(f"{cid}/{key}: rationale required for {verdict}")
            quote = check.get("quote")
            if quote is not None and (not isinstance(quote, str) or not quote.strip() or quote not in text):
                raise ValueError(f"{cid}/{key}: quoted evidence is absent from transcript")
            mode = next(c["mode"] for c in case["checks"] if c["id"] == key)
            if verdict == "pass" and mode == "presence" and not quote:
                raise ValueError(f"{cid}/{key}: positive pass requires exact transcript quote")
            by_id[key] = verdict

        results = [by_id.get(c["id"], "uncertain") for c in case["checks"]]
        status = ("FAILED" if "fail" in results else
                  "INCOMPLETE" if "uncertain" in results else "PASSED")
        summary[status.lower()] += 1
        summary["details"].append({"case_id": cid, "status": status,
                                   "checks_passed": results.count("pass"),
                                   "checks_total": len(results)})
    if summary["failed"]:
        summary["status"] = "FAILED"
    elif summary["incomplete"]:
        summary["status"] = "INCOMPLETE"
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "evals/requirements/cases.json")
    parser.add_argument("--observations", type=Path,
                        help="Reviewer evidence JSON; omitted means catalog-only validation")
    args = parser.parse_args()
    try:
        catalog = load_catalog(args.catalog)
        if args.observations is None:
            print(f"VALID catalog: {len(catalog['cases'])} Requirements cases; "
                  "no agent behavior has been evaluated.")
            return 0
        observations = json.loads(args.observations.read_text(encoding="utf-8"))
        result = evaluate(catalog, observations, args.observations.parent)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return {"PASSED": 0, "FAILED": 1, "INCOMPLETE": 2}[result["status"]]
    except (ValueError, OSError, json.JSONDecodeError, TypeError) as exc:
        print(f"INVALID evaluation: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
