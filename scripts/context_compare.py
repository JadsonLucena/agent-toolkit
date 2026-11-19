#!/usr/bin/env python3
"""Compare independently assessed context runs; never infer agent success.

Inputs are externally observed assessments. This script only validates records
and compares matched runs; it neither launches an LLM nor verifies tool traces.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

VALID_STRATEGIES = {"native", "structural", "sqlite-fts5", "semantic", "ai-memory"}
VALID_VERDICTS = {"pass", "fail", "incomplete"}
VALID_CACHE = {"cold", "warm"}
REQUIRED = {
    "case_id", "strategy", "iteration", "model", "harness", "repository_sha",
    "source_baseline_ref", "authority_ref", "cache_state", "verdict",
}
DELIVERY_REUSE = {"DL-05", "DL-08", "DL-25", "DL-26", "DL-27"}


class ComparisonError(ValueError):
    pass


def _integer(entry, name):
    value = entry.get(name)
    if value is not None and (type(value) is not int or value < 0):
        raise ComparisonError(name + " must be a non-negative integer when measured")
    return value


def evaluate_runs(payload: dict, known_cases: set[str]) -> dict:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ComparisonError("expected version 1 comparison dataset")
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise ComparisonError("runs must be an array")
    seen = set()
    grouped = defaultdict(dict)
    totals = defaultdict(lambda: {"pass": 0, "fail": 0, "incomplete": 0})
    for run in runs:
        if not isinstance(run, dict) or REQUIRED - run.keys():
            raise ComparisonError("run missing required matching fields")
        for field in ("case_id", "model", "harness", "repository_sha",
                      "source_baseline_ref", "authority_ref"):
            if not isinstance(run[field], str) or not run[field].strip():
                raise ComparisonError("invalid " + field)
        if run["case_id"] not in known_cases:
            raise ComparisonError("unknown context evaluation case: " + run["case_id"])
        if run["strategy"] not in VALID_STRATEGIES:
            raise ComparisonError("unknown retrieval strategy")
        if run["verdict"] not in VALID_VERDICTS:
            raise ComparisonError("unknown assessment verdict")
        if run["cache_state"] not in VALID_CACHE:
            raise ComparisonError("cache_state must be cold or warm")
        if type(run["iteration"]) is not int or run["iteration"] < 1:
            raise ComparisonError("iteration must be a positive integer")
        for metric in ("tokens", "elapsed_ms", "index_ms", "required_obligations",
                       "verified_obligations"):
            _integer(run, metric)
        if (run.get("required_obligations") is not None and
                run.get("verified_obligations") is not None and
                run["verified_obligations"] > run["required_obligations"]):
            raise ComparisonError("verified obligations cannot exceed required")
        if run["verdict"] != "incomplete":
            for field in ("reviewer", "trace_ref"):
                if not isinstance(run.get(field), str) or not run[field].strip():
                    raise ComparisonError("a completed assessment needs reviewer and trace_ref")
        key = tuple(run[f] for f in (
            "case_id", "iteration", "model", "harness", "repository_sha",
            "source_baseline_ref", "authority_ref", "cache_state",
        ))
        unique = (key, run["strategy"])
        if unique in seen:
            raise ComparisonError("duplicate run for strategy and matched fixture")
        seen.add(unique)
        grouped[key][run["strategy"]] = run
        totals[run["strategy"]][run["verdict"]] += 1

    pairs = []
    unmatched = 0
    for key, candidates in grouped.items():
        native = candidates.get("native")
        for strategy, candidate in candidates.items():
            if strategy == "native":
                continue
            if native is None:
                unmatched += 1
                continue
            record = {
                "case_id": candidate["case_id"],
                "strategy": strategy,
                "iteration": candidate["iteration"],
                "model": candidate["model"],
                "harness": candidate["harness"],
                "repository_sha": candidate["repository_sha"],
                "source_baseline_ref": candidate["source_baseline_ref"],
                "authority_ref": candidate["authority_ref"],
                "cache_state": candidate["cache_state"],
                "native_verdict": native["verdict"],
                "candidate_verdict": candidate["verdict"],
                "native_trace_ref": native.get("trace_ref"),
                "candidate_trace_ref": candidate.get("trace_ref"),
            }
            for metric in ("tokens", "elapsed_ms", "index_ms",
                           "verified_obligations"):
                a, b = native.get(metric), candidate.get(metric)
                record[metric + "_delta"] = b - a if a is not None and b is not None else None
            pairs.append(record)

    return {
        "status": "observations-only" if runs else "no-observations",
        "runs": len(runs),
        "strategies": dict(sorted(totals.items())),
        "matched_pairs": sorted(pairs, key=lambda r: (
            r["case_id"], r["iteration"], r["strategy"], r["model"],
            r["harness"], r["repository_sha"], r["source_baseline_ref"],
            r["authority_ref"], r["cache_state"],
        )),
        "unmatched_candidates": unmatched,
        "limitations": [
            "This script does not run or grade an agent; supplied verdicts require independent trace review.",
            "Unknown metrics remain null, not zero.",
            "Different models, revisions, authority, iteration or cache state are not paired.",
            "Per-pair deltas are descriptive, not statistical significance or causal proof.",
        ],
    }


def load_case_ids(root: Path) -> set[str]:
    context = json.loads((root / "evals/context/cases.json").read_text(encoding="utf-8"))
    delivery = json.loads((root / "evals/delivery/cases.json").read_text(encoding="utf-8"))
    ids = {case["id"] for case in context["cases"]}
    present = {case["id"] for case in delivery["cases"]}
    if not DELIVERY_REUSE.issubset(present):
        raise ComparisonError("required Delivery evaluations are unavailable")
    return ids | DELIVERY_REUSE


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=Path, required=True, help="JSON record of assessed host runs")
    args = ap.parse_args()
    try:
        root = Path(__file__).resolve().parents[1]
        data = json.loads(args.runs.read_text(encoding="utf-8"))
        report = evaluate_runs(data, load_case_ids(root))
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["status"] == "observations-only" else 2
    except (OSError, json.JSONDecodeError, ComparisonError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
