#!/usr/bin/env python3
"""Build one disposable Testing Review fixture as a frozen two-commit Git repository.

No model is invoked. Never overwrite an existing case directory.
"""
import argparse
import json
from pathlib import Path
import subprocess

CATALOG = Path(__file__).with_name("testing-cases.json")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def write(repo, relative, content):
    destination = repo / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build(case_id, output):
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    case = next((item for item in catalog["cases"] if item["id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown case: {case_id}")
    fixture = case["fixture"]
    folder = output.resolve() / case_id
    if folder.exists():
        raise FileExistsError(f"refusing to overwrite: {folder}")
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.mkdir()

    subprocess.run(["git", "init", "-q", "-b", "main", str(folder)],
                   check=True, capture_output=True, text=True)
    git(folder, "config", "user.name", "Testing Fixture")
    git(folder, "config", "user.email", "fixture@example.invalid")
    write(folder, "docs/accepted-behavior.md", fixture["contract"])
    write(folder, "src/__init__.py", "")
    write(folder, "tests/__init__.py", "")
    write(folder, "src/service.py", fixture["base"])
    write(folder, "tests/test_service.py", fixture["tests"])
    if "witness" in fixture:
        write(folder, "witness/test_contract.py", fixture["witness"])
    git(folder, "add", ".")
    git(folder, "commit", "-q", "-m", "test: establish baseline and test evidence")
    base = git(folder, "rev-parse", "HEAD")

    write(folder, "src/service.py", fixture["head"])
    if fixture.get("ci_stale"):
        write(folder, "ci/check.json", json.dumps({
            "status": "success", "head_sha": base,
            "note": "historical result; not evidence for the new head"
        }, indent=2) + "\n")
    git(folder, "add", ".")
    git(folder, "commit", "-q", "-m", "test: change under review")
    head = git(folder, "rev-parse", "HEAD")
    return {"case_id": case_id, "repository": str(folder),
            "base_sha": base, "head_sha": head,
            "contract": "docs/accepted-behavior.md",
            "code": "src/service.py", "tests": "tests/test_service.py",
            "witness": "witness/test_contract.py" if "witness" in fixture else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.case, args.out), indent=2))
    except (ValueError, FileExistsError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"Cannot build fixture: {exc}\n")


if __name__ == "__main__":
    main()
