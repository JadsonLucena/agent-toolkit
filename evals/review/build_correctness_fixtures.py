#!/usr/bin/env python3
"""Materialize one read-only review benchmark as a disposable two-commit Git repo.

Never runs an agent or claims a review outcome. The destination case directory
must not exist, so existing user data cannot be overwritten.
"""
import argparse
import json
import subprocess
from pathlib import Path


CATALOG = Path(__file__).with_name("correctness-cases.json")


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def write(repo, path, content):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build(case_id, output):
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    case = next((c for c in catalog["cases"] if c["id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown case: {case_id}")
    fixture = case["fixture"]
    if fixture["path"] != "src/logic.py":
        raise ValueError("fixture code path is not allowed")

    repository = output.resolve() / case_id
    if repository.exists():
        raise FileExistsError(f"refusing to overwrite: {repository}")
    repository.parent.mkdir(parents=True, exist_ok=True)
    repository.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repository)],
                   check=True, capture_output=True, text=True)
    git(repository, "config", "user.email", "fixture@example.invalid")
    git(repository, "config", "user.name", "Correctness Fixture")

    write(repository, "docs/accepted-behavior.md", fixture["contract"])
    write(repository, fixture["path"], fixture["base"])
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "test: established baseline")
    base_sha = git(repository, "rev-parse", "HEAD")

    write(repository, fixture["path"], fixture["changed"])
    if "head_tests" in fixture:
        write(repository, "tests/test_logic.py", fixture["head_tests"])
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "test: change under review")
    head_sha = git(repository, "rev-parse", "HEAD")
    return {"case_id": case_id, "repository": str(repository),
            "base_sha": base_sha, "head_sha": head_sha,
            "contract": "docs/accepted-behavior.md",
            "code": fixture["path"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="CR-01, CR-02, ...")
    parser.add_argument("--out", type=Path, required=True,
                        help="Disposable parent directory (case subdir must not exist)")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.case, args.out), indent=2))
    except (ValueError, FileExistsError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Cannot build fixture: {error}\n")


if __name__ == "__main__":
    main()
