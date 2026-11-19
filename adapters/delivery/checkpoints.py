"""Optional durable Delivery checkpoint metadata and external-effect journal.

Never grants authorizations or replays operations. Must reconcile fresh Git,
source, approvals and external effects before any resumed mutation.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path

try:
    import sqlite3
except ImportError:  # Optional in some Python installations.
    sqlite3 = None

from adapters.context.native import ContextError, _repository, verify_context

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
HASH = re.compile(r"^[a-f0-9]{64}$")
FIELDS = frozenset({
    "execution_id", "repository", "context_id", "slice_ref",
    "stage", "target_stage", "head_sha", "source_baseline_ref",
    "source_versions", "evidence_refs", "pending_decisions",
    "blockers", "next_owner", "authorization_ref",
})
REQUIRED = {"execution_id", "repository", "context_id",
            "stage", "target_stage", "head_sha"}
EFFECT_STATES = {"planned", "unknown", "confirmed"}


class CheckpointError(ValueError):
    """Unsafe persistence, invalid checkpoint, or conflicting generation."""


def _id(value: object, name: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise CheckpointError("invalid " + name)
    return value


def _snapshot(value: dict) -> dict:
    if not isinstance(value, dict) or not REQUIRED.issubset(value):
        raise CheckpointError("checkpoint missing required fields")
    if set(value) - FIELDS:
        raise CheckpointError("unsupported checkpoint fields; raw transcripts are prohibited")
    for key in ("execution_id", "context_id", "stage", "target_stage"):
        _id(value[key], key)
    if not isinstance(value["repository"], str) or not Path(value["repository"]).is_absolute():
        raise CheckpointError("repository must be an absolute Git root")
    if not isinstance(value["head_sha"], str) or not re.fullmatch(r"[0-9a-f]{40,64}", value["head_sha"]):
        raise CheckpointError("head_sha must be a complete Git commit")
    for key in ("slice_ref", "source_baseline_ref", "next_owner", "authorization_ref"):
        if key in value and value[key] is not None:
            _id(value[key], key)
    for key in ("evidence_refs", "pending_decisions", "blockers"):
        if key in value:
            items = value[key]
            if not isinstance(items, list) or len(items) > 40 or any(
                not isinstance(v, str) or not v or len(v) > 256 for v in items
            ):
                raise CheckpointError("invalid " + key)
    versions = value.get("source_versions")
    if not isinstance(versions, list) or not 1 <= len(versions) <= 80:
        raise CheckpointError("source_versions must be a nonempty, bounded list")
    seen = set()
    for source in versions:
        if not isinstance(source, dict) or set(source) != {"ref", "sha256", "critical"}:
            raise CheckpointError("source versions require only ref, sha256, critical")
        if (not isinstance(source["ref"], str) or len(source["ref"]) > 1024 or
                not HASH.fullmatch(str(source["sha256"])) or
                type(source["critical"]) is not bool or source["ref"] in seen):
            raise CheckpointError("invalid or duplicate source version")
        seen.add(source["ref"])
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(encoded.encode("utf-8")) > 16384:
        raise CheckpointError("checkpoint exceeds bounded metadata size")
    return json.loads(encoded)


def snapshot_from_pack(
    pack: dict, execution_id: str, context_id: str,
    stage: str, target_stage: str, **metadata
) -> dict:
    if (pack.get("status") != "ready" or pack.get("missing_critical")
            or not pack.get("sources")):
        raise CheckpointError("cannot checkpoint missing or incomplete source evidence")
    snapshot = {
        "execution_id": execution_id,
        "context_id": context_id,
        "repository": pack["repository"],
        "head_sha": pack["head_sha"],
        "stage": stage,
        "target_stage": target_stage,
        "source_versions": [
            {"ref": s["ref"], "sha256": s["sha256"], "critical": bool(s["critical"])}
            for s in pack["sources"]
        ],
    }
    snapshot.update(metadata)
    return _snapshot(snapshot)


def _verify_recorded_sources(snapshot: dict) -> dict:
    root, head = _repository(Path(snapshot["repository"]))
    if head != snapshot["head_sha"]:
        raise CheckpointError("checkpoint head does not match current Git HEAD")
    result = verify_context(root, {
        "kind": "context-pack", "schema_version": 1,
        "repository": str(root), "head_sha": snapshot["head_sha"],
        "sources": snapshot.get("source_versions", []),
        "missing_critical": [],
    })
    if result["status"] != "unchanged":
        raise CheckpointError("checkpoint contains stale or unverified source versions")
    return result



SCHEMA_SQL = (
    """CREATE TABLE IF NOT EXISTS checkpoints (
        execution_id TEXT PRIMARY KEY,
        generation INTEGER NOT NULL CHECK(generation > 0),
        snapshot_json TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS effects (
        execution_id TEXT NOT NULL REFERENCES checkpoints(execution_id),
        effect_id TEXT NOT NULL,
        operation TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('planned','unknown','confirmed')),
        evidence_ref TEXT,
        PRIMARY KEY(execution_id, effect_id)
    )""",
    """CREATE TABLE IF NOT EXISTS effect_history (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT NOT NULL,
        effect_id TEXT NOT NULL,
        status TEXT NOT NULL,
        evidence_ref TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
)


def _schema_objects(connection) -> dict[str, str]:
    return dict(connection.execute(
        "SELECT name,sql FROM sqlite_master "
        "WHERE type IN ('table','index','view','trigger') AND name NOT LIKE 'sqlite_%'"
    ))


def _initialize_schema(connection) -> None:
    """Recover only exact partial first-time schemas; version change is atomic."""
    with sqlite3.connect(":memory:") as reference:
        for statement in SCHEMA_SQL:
            reference.execute(statement)
        expected = _schema_objects(reference)
    connection.execute("BEGIN IMMEDIATE")
    try:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise CheckpointError("unknown checkpoint database schema")
        existing = _schema_objects(connection)
        if any(expected.get(name) != sql for name, sql in existing.items()):
            raise CheckpointError("unrecognized or modified checkpoint schema")
        if version == 1 and existing != expected:
            raise CheckpointError("checkpoint schema is incomplete or modified")
        if version == 0:
            # A previous process may have stopped after any CREATE TABLE.
            # Only the exact expected schema prefix can be completed.
            for statement in SCHEMA_SQL:
                connection.execute(statement)
            connection.execute("PRAGMA user_version = 1")
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise

class CheckpointStore:
    def __init__(self, db_path: Path):
        if sqlite3 is None:
            raise CheckpointError("SQLite unavailable; durable checkpoint disabled")
        path = Path(db_path).expanduser()
        if not path.is_absolute() or not path.parent.is_dir():
            raise CheckpointError("database requires an explicit absolute path and existing private directory")
        # Private local state; do not make a database inside the source tree.
        parent = path.parent
        if parent.is_symlink() or (os.name == "posix" and
                                   stat.S_IMODE(parent.stat().st_mode) & 0o077):
            raise CheckpointError("checkpoint directory must be private (0700)")
        if path.is_symlink():
            raise CheckpointError("database must not be a symlink")
        try:
            if not path.exists():
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
            elif os.name == "posix" and (stat.S_IMODE(path.stat().st_mode) & 0o077):
                raise CheckpointError("existing database must be owner-only (0600)")
            # Resolve the entire parent chain, not only the immediate directory:
            # aliases could otherwise place the DB inside the source tree.
            self.path = path.resolve()
            self.db = sqlite3.connect(self.path, isolation_level=None, timeout=3.0)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA foreign_keys = ON")
            self.db.execute("PRAGMA busy_timeout = 3000")
            self.db.execute("PRAGMA journal_mode = WAL")
            _initialize_schema(self.db)
        except OSError as exc:
            if hasattr(self, "db"):
                self.db.close()
            raise CheckpointError("cannot create private checkpoint database") from exc
        except BaseException:
            if hasattr(self, "db"):
                self.db.close()
            raise

    def close(self) -> None:
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def save(self, snapshot: dict, *, expected_generation: int = 0) -> int:
        record = _snapshot(snapshot)
        if self.path.resolve().is_relative_to(Path(record["repository"]).resolve()):
            raise CheckpointError("checkpoint database must be outside the source repository")
        _verify_recorded_sources(record)
        if type(expected_generation) is not int or expected_generation < 0:
            raise CheckpointError("invalid expected_generation")
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT generation FROM checkpoints WHERE execution_id = ?",
                (record["execution_id"],),
            ).fetchone()
            actual = row["generation"] if row else 0
            if actual != expected_generation:
                raise CheckpointError("checkpoint generation conflict")
            next_gen = actual + 1
            if row:
                self.db.execute("""
                    UPDATE checkpoints SET generation=?, snapshot_json=?,
                        updated_at=CURRENT_TIMESTAMP WHERE execution_id=?
                """, (next_gen, payload, record["execution_id"]))
            else:
                self.db.execute("""
                    INSERT INTO checkpoints(execution_id,generation,snapshot_json)
                    VALUES(?,?,?)
                """, (record["execution_id"], next_gen, payload))
            self.db.execute("COMMIT")
            return next_gen
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def load(self, execution_id: str) -> tuple[dict, int]:
        row = self.db.execute(
            "SELECT snapshot_json,generation FROM checkpoints WHERE execution_id=?",
            (_id(execution_id, "execution_id"),),
        ).fetchone()
        if row is None:
            raise CheckpointError("checkpoint not found")
        return _snapshot(json.loads(row["snapshot_json"])), row["generation"]

    def record_effect(
        self, execution_id: str, effect_id: str, operation: str,
        status: str, evidence_ref: str | None = None,
    ) -> None:
        execution_id = _id(execution_id, "execution_id")
        effect_id = _id(effect_id, "effect_id")
        operation = _id(operation, "operation")
        if status not in EFFECT_STATES:
            raise CheckpointError("unsupported effect status")
        if status == "confirmed" and not evidence_ref:
            raise CheckpointError("confirmed effect requires independently checked evidence reference")
        if evidence_ref is not None and (
            not isinstance(evidence_ref, str) or len(evidence_ref) > 256
        ):
            raise CheckpointError("invalid evidence reference")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if not self.db.execute(
                "SELECT 1 FROM checkpoints WHERE execution_id=?", (execution_id,)
            ).fetchone():
                raise CheckpointError("execution checkpoint not found")
            row = self.db.execute(
                "SELECT operation,status,evidence_ref FROM effects WHERE execution_id=? AND effect_id=?",
                (execution_id, effect_id),
            ).fetchone()
            if row is None:
                if status != "planned":
                    raise CheckpointError("effect must be journaled as planned before execution")
                self.db.execute("""
                    INSERT INTO effects(execution_id,effect_id,operation,status,evidence_ref)
                    VALUES(?,?,?,?,NULL)
                """, (execution_id, effect_id, operation, status))
            else:
                if row["operation"] != operation:
                    raise CheckpointError("effect identity reused for another operation")
                old = row["status"]
                if old == status:
                    if row["evidence_ref"] != evidence_ref:
                        raise CheckpointError("conflicting repeated effect observation")
                    self.db.execute("COMMIT")
                    return
                if (old, status) not in {
                    ("planned", "unknown"), ("planned", "confirmed"),
                    ("unknown", "confirmed")
                }:
                    raise CheckpointError("effect cannot transition backwards or replay")
                self.db.execute("""
                    UPDATE effects SET status=?, evidence_ref=?
                    WHERE execution_id=? AND effect_id=?
                """, (status, evidence_ref, execution_id, effect_id))
            self.db.execute("""
                INSERT INTO effect_history(execution_id,effect_id,status,evidence_ref)
                VALUES(?,?,?,?)
            """, (execution_id, effect_id, status, evidence_ref))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def resume(self, execution_id: str, repo: Path) -> dict:
        snapshot, generation = self.load(execution_id)
        if Path(repo).resolve() != Path(snapshot["repository"]).resolve():
            raise CheckpointError("checkpoint belongs to a different repository")
        root, _ = _repository(Path(repo))
        if snapshot["repository"] != str(root):
            raise CheckpointError("checkpoint belongs to a different repository")
        inspection = verify_context(root, {
            "kind": "context-pack", "schema_version": 1,
            "repository": str(root), "head_sha": snapshot["head_sha"],
            "sources": snapshot.get("source_versions", []),
            "missing_critical": [],
        })
        effects = [
            dict(row) for row in self.db.execute(
                "SELECT effect_id,operation,status,evidence_ref FROM effects "
                "WHERE execution_id=? ORDER BY effect_id", (execution_id,),
            ).fetchall()
        ]
        unresolved = [v for v in effects if v["status"] != "confirmed"]
        source_status = {r["ref"]: r["status"] for r in inspection["sources"]}
        critical_missing = [
            item["ref"] for item in snapshot.get("source_versions", [])
            if item["critical"] and source_status.get(item["ref"]) != "unchanged"
        ]
        if unresolved or critical_missing:
            state = "blocked"
        elif inspection["status"] != "unchanged":
            state = "revalidate"
        else:
            state = "inspect-only"
        return {
            "status": state,
            "generation": generation,
            "snapshot": snapshot,
            "source_verification": inspection,
            "effects": effects,
            "unresolved_effects": unresolved,
            "critical_sources_stale": critical_missing,
            "authorization": "must-revalidate-current-authority",
            "execution": "never-automatic-replay",
            "note": "A saved stage or permission is not authorization or proof of an external effect.",
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True, type=Path)
    sub = ap.add_subparsers(dest="command", required=True)
    save = sub.add_parser("save")
    save.add_argument("--snapshot", required=True, type=Path)
    save.add_argument("--expected-generation", type=int, default=0)
    effect = sub.add_parser("effect")
    effect.add_argument("--execution-id", required=True)
    effect.add_argument("--effect-id", required=True)
    effect.add_argument("--operation", required=True)
    effect.add_argument("--status", required=True, choices=sorted(EFFECT_STATES))
    effect.add_argument("--evidence-ref")
    resume = sub.add_parser("resume")
    resume.add_argument("--execution-id", required=True)
    resume.add_argument("--repo", required=True, type=Path)
    args = ap.parse_args()
    try:
        with CheckpointStore(args.db) as store:
            if args.command == "save":
                snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
                outcome = {"status": "saved", "generation": store.save(
                    snapshot, expected_generation=args.expected_generation)}
            elif args.command == "effect":
                store.record_effect(args.execution_id, args.effect_id,
                                    args.operation, args.status, args.evidence_ref)
                outcome = {"status": "recorded"}
            else:
                outcome = store.resume(args.execution_id, args.repo)
        print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
        return 2 if outcome["status"] == "blocked" else 0
    except (CheckpointError, ContextError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
