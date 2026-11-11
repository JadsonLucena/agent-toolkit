"""Task-team contract tests: frozen identity, proportional N, observed transport."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "review"))
from prepare_context import prepare_context  # noqa: E402
import team_orchestration as team  # noqa: E402
from evidence_validation import validate_evidence  # noqa: E402


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()


class FakeTaskHost:
    def __init__(self, *, requests=False, observe_direct=False, wrong_target=False, bad_verifier=False,
                 audit_subject="Can retries race?"):
        self.batches = []
        self.resumed = []
        self.requests = requests
        self.observe_direct = observe_direct
        self.wrong_target = wrong_target
        self.bad_verifier = bad_verifier
        self.audit_subject = audit_subject
        self.by_role = {}
        self.last_review_id = None

    async def task_batch(self, requests):
        self.batches.append(requests)
        answers = []
        for request in requests:
            role = request["role"]
            task_id = f"isolated-{role}"
            self.by_role[role] = task_id
            self.last_review_id = request["review_id"]
            target = dict(request["target"])
            if self.wrong_target:
                target["head_sha"] = "stale"
            reply = {
                "task_id": task_id, "role": role, "review_id": request["review_id"],
                "repository": request["repository"], "target": target,
                "reviewed_files": list(request["changed_files"]),
                "verified_head_sha": request["target"]["head_sha"],
                "candidate_findings": [], "uncertainties": [], "relay_requests": [],
            }
            if self.requests and role == "correctness-reviewer":
                reply["relay_requests"] = [{
                    "recipient_role": "reliability-reviewer", "kind": "challenge",
                    "subject": "Can two charges race?",
                    "requested_action": "Trace idempotency guard",
                    "evidence_refs": ["payments.py:5"],
                }]
            if role == "finding-verifier":
                reply["verification_method"] = "votes" if self.bad_verifier else "source-inspection"
                reply["inspected_files"] = list(request["changed_files"])
                reply["verified_findings"] = []
            answers.append(reply)
        return answers

    async def resume(self, task_id, message):
        self.resumed.append((task_id, message))
        role = task_id.removeprefix("isolated-")
        return {
            "role": role, "review_id": message["review_id"],
            "repository": self._repository, "target": self._target,
            "kind": "response" if message["kind"] == "challenge" else "resolution",
            "subject": "Evidence examined", "evidence_refs": ["payments.py:5"],
        }

    async def direct_message_audit(self, review_id):
        if not self.observe_direct:
            return []
        sender = self.by_role["correctness-reviewer"]
        recipient = self.by_role["reliability-reviewer"]
        return [
            {"review_id": review_id, "via": "direct-peer", "status": "delivered",
             "kind": "challenge", "thread_id": "direct-1", "message_id": "a",
             "subject": self.audit_subject, "evidence_refs": ["payments.py:1"],
             "sender_task_id": sender, "recipient_task_id": recipient},
            {"review_id": review_id, "via": "direct-peer", "status": "delivered",
             "kind": "response", "thread_id": "direct-1", "message_id": "b",
             "response_to": "a", "subject": "Inspected the guard", "evidence_refs": ["payments.py:1"],
             "sender_task_id": recipient, "recipient_task_id": sender},
        ]


class TeamOrchestrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "payments.py").write_text("amount=1\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "payments.py").write_text("amount=2\n")
        (self.repo / "tests.py").write_text("assert True\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "feature")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.ctx = prepare_context(self.repo, base=self.base, head=self.head, allow_ocr=False)

    def plan(self, risk="R3", concerns=None, tasks=True, direct=False, implementer=False):
        if concerns is None:
            concerns = ["correctness", "reliability", "security"]
        return team.freeze(
            self.ctx, self.repo, risk_profile=risk, concerns=concerns,
            task_available=tasks, isolated_tasks=tasks,
            direct_peer_supported=direct, lead_implemented_change=implementer,
            review_id="review-a",
        )

    def host(self, **kwargs):
        host = FakeTaskHost(**kwargs)
        host._repository = str(self.repo.resolve())
        host._target = dict(self.ctx["target"])
        return host

    async def test_r0_native_zero_lenses(self):
        plan = self.plan("R0", ["correctness"], tasks=True)
        self.assertEqual([], plan["selected_roles"])
        self.assertEqual("native-solo", plan["execution_mode"])
        result = await team.execute(plan, None)
        self.assertEqual([], result["team_members"])
        self.assertEqual("not-required", result["independent_verification"]["mode"])

    async def test_r1_zero_or_one_only(self):
        solo = self.plan("R1", [], tasks=True)
        self.assertEqual([], solo["selected_roles"])
        one = self.plan("R1", ["testing", "correctness"], tasks=True)
        self.assertEqual(["testing-reviewer"], one["selected_roles"])

    async def test_r2_uses_2_to_4_distinct_specialists(self):
        plan = self.plan("R2", ["correctness", "reliability", "security", "testing", "architecture"])
        self.assertEqual(4, len(plan["selected_roles"]))
        self.assertIn("architecture-reviewer", plan["omitted_roles"])

    async def test_r3_uses_3_to_5_and_isolated_verifier_always(self):
        plan = self.plan("R3", ["correctness", "reliability", "security", "testing", "architecture", "contract"])
        self.assertEqual(5, len(plan["selected_roles"]))
        self.assertIn("specification-reviewer", plan["omitted_roles"])
        host = self.host()
        result = await team.execute(plan, host)
        self.assertEqual(5, len(host.batches[0]))
        self.assertEqual(1, len(host.batches[1]))
        self.assertEqual("finding-verifier", host.batches[1][0]["role"])
        self.assertEqual("isolated-agent", result["independent_verification"]["mode"])
        self.assertEqual(None, result["review_status"])
        self.assertFalse(result["coordination"]["real_peer_delivery_observed"])

    async def test_r2_single_all_purpose_agent_is_rejected(self):
        with self.assertRaisesRegex(team.TeamPlanningError, "2-4 distinct concerns"):
            self.plan("R2", ["correctness"])

    async def test_r3_two_real_concerns_are_allowed_with_verifier(self):
        plan = self.plan("R3", ["security", "correctness"])
        self.assertEqual(2, len(plan["selected_roles"]))
        self.assertTrue(plan["n_justification"]["below_ideal_range"])
        self.assertTrue(plan["verifier_required"])

    async def test_no_tasks_falls_back_to_real_native_solo(self):
        plan = self.plan(tasks=False)
        self.assertEqual("native-solo", plan["execution_mode"])
        self.assertEqual([], plan["selected_roles"])
        result = await team.execute(plan, None)
        self.assertEqual([], result["team_members"])
        self.assertEqual("native-second-pass", result["independent_verification"]["mode"])

    async def test_task_without_messaging_is_team_relayed_not_native_solo(self):
        plan = self.plan(concerns=["correctness", "reliability", "testing"])
        host = self.host(requests=True)
        result = await team.execute(plan, host)
        self.assertEqual("team-relayed", result["execution_mode"])
        self.assertEqual(3, len(host.batches[0]))
        self.assertEqual(2, len(host.resumed))
        self.assertEqual("isolated-reliability-reviewer", host.resumed[0][0])
        self.assertEqual("isolated-correctness-reviewer", host.resumed[1][0])
        self.assertEqual(["challenge", "response", "resolution"], [m["kind"] for m in result["peer_threads"]])
        self.assertEqual([], result["unresolved_questions"])
        for task in host.batches[0]:
            self.assertEqual(plan["target"], task["target"])
            self.assertEqual("review-a", task["review_id"])
            self.assertIn("# ", task["agent_prompt"])

    async def test_claimed_direct_capability_without_delivery_is_relayed(self):
        plan = self.plan(concerns=["correctness", "reliability", "testing"], direct=True)
        host = self.host(requests=True)
        result = await team.execute(plan, host)
        self.assertEqual("team-relayed", result["execution_mode"])
        self.assertFalse(result["coordination"]["real_peer_delivery_observed"])

    async def test_real_observed_direct_challenge_and_response_is_live(self):
        plan = self.plan(concerns=["correctness", "reliability", "testing"], direct=True)
        host = self.host(observe_direct=True)
        result = await team.execute(plan, host)
        self.assertEqual("team-live", result["execution_mode"])
        self.assertTrue(result["coordination"]["real_peer_delivery_observed"])
        self.assertEqual(2, len(result["peer_threads"]))
        self.assertEqual([], host.resumed)

    async def test_r1_nonblocking_observation_does_not_spawn_verifier(self):
        plan = self.plan("R1", ["correctness"])
        host = self.host()
        original = host.task_batch

        async def first_pass(requests):
            answers = await original(requests)
            if requests[0]["role"] != "finding-verifier":
                answers[0]["candidate_findings"] = [
                    {"finding_id": "low-1", "severity": "low", "confidence": "medium",
                     "location": "payments.py:1", "claim": "Sample low-impact concern",
                     "trigger": "test", "evidence": "payments.py:1",
                     "consequence": "none", "blocking": False},
                ]
            return answers

        host.task_batch = first_pass
        result = await team.execute(plan, host)
        self.assertEqual(1, len(host.batches))
        self.assertEqual("not-required", result["independent_verification"]["mode"])

    async def test_resume_unavailable_uses_new_narrow_task_and_records_ids(self):
        plan = self.plan("R2", ["correctness", "reliability"])
        host = self.host(requests=True)
        original = host.task_batch
        narrow_calls = []

        async def new_task(requests):
            if "relayed_message" not in requests[0]:
                return await original(requests)
            req = requests[0]
            narrow_calls.append(req)
            msg = req["relayed_message"]
            return [{
                "role": req["role"], "review_id": req["review_id"],
                "target": req["target"], "repository": req["repository"],
                "task_id": "new-" + req["role"],
                "kind": "response" if msg["kind"] == "challenge" else "resolution",
                "subject": "Inspected source", "evidence_refs": ["payments.py:1"],
            }]

        async def no_resume(task_id, msg):
            raise NotImplementedError("host has Task but not resume")

        host.task_batch = new_task
        host.resume = no_resume
        result = await team.execute(plan, host)
        self.assertEqual("team-relayed", result["execution_mode"])
        self.assertEqual("Task+new Task", result["coordination"]["transport"])
        self.assertEqual(2, len(narrow_calls))
        self.assertEqual([], result["unresolved_questions"])
        self.assertTrue(any(m.get("recipient_task_id") for m in result["peer_threads"]))

    async def test_stale_specialist_is_rejected(self):
        plan = self.plan()
        with self.assertRaisesRegex(team.TeamPlanningError, "stale"):
            await team.execute(plan, self.host(wrong_target=True))

    async def test_verifier_cannot_be_a_vote(self):
        plan = self.plan()
        with self.assertRaisesRegex(team.TeamPlanningError, "not independently isolated or source"):
            await team.execute(plan, self.host(bad_verifier=True))

    async def test_lead_only_passes_after_complete_reconciliation(self):
        plan = self.plan()
        result = await team.execute(plan, self.host())
        proof = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("PASS", proof["review_status"])
        incomplete = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=["payments.py"],
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("INCOMPLETE", incomplete["review_status"])

    async def test_blocker_requires_lead_source_confirmation_before_fail(self):
        plan = self.plan()
        result = await team.execute(plan, self.host())
        evidence = {
            "finding_id": "F1", "verification_status": "confirmed",
            "location": "payments.py:1", "lead_confirmed": False,
        }
        incomplete = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[evidence], unresolved_material=[],
        )
        self.assertEqual("INCOMPLETE", incomplete["review_status"])
        self.assertIn("lead-confirmed", str(incomplete["unresolved_questions"]))
        evidence["lead_confirmed"] = True
        failed = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[evidence], unresolved_material=[],
        )
        self.assertEqual("FAIL", failed["review_status"])

    async def test_explicit_nonmaterial_questions_do_not_prevent_advisory_pass(self):
        plan = self.plan()
        result = await team.execute(plan, self.host())
        clean = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[],
            unresolved_material=[{"question": "Optional display wording", "material": False}],
        )
        self.assertEqual("PASS", clean["review_status"])
        self.assertEqual(1, len(clean["unresolved_questions"]))

    async def test_likelihood_metadata_is_optional_but_invalid_values_rejected(self):
        valid = {
            "finding_id": "F1", "location": "payments.py:1",
            "claim": "Concurrent commit", "trigger": "retry",
            "evidence": "payments.py:1", "consequence": "duplicate",
            "severity": "high", "confidence": "medium",
            "likelihood": "low", "origin": "amplified-pre-existing",
            "amplification_reason": "New financial operation",
            "disposition": "decision-needed",
        }
        team._validate_finding(valid, {"payments.py"})
        valid["likelihood"] = "guaranteed"
        with self.assertRaisesRegex(team.TeamPlanningError, "likelihood"):
            team._validate_finding(valid, {"payments.py"})

    async def test_advisory_lead_can_report_complete_advisory_pass(self):
        plan = self.plan(implementer=True)
        self.assertEqual("advisory", plan["review_profile"])
        result = await team.execute(plan, self.host())
        final = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=False, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("PASS", final["review_status"])
        self.assertEqual("advisory", final["review_profile"])
        self.assertFalse(final["reviewer_independent"])

    async def test_implementer_lead_never_passes_even_with_isolated_team(self):
        self.ctx["review_profile"] = "gate"
        plan = self.plan(implementer=True)
        result = await team.execute(plan, self.host())
        proof = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=False, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("INCOMPLETE", proof["review_status"])
        self.assertFalse(proof["reviewer_independent"])

    async def test_workspace_mutation_invalidates_snapshot(self):
        (self.repo / "untracked.txt").write_text("initial\n")
        ctx = prepare_context(self.repo, allow_ocr=False)
        self.assertIn("workspace_fingerprint_sha256", ctx["target"])
        frozen = team.freeze(ctx, self.repo, risk_profile="R0",
                             concerns=[], task_available=False, isolated_tasks=False)
        result = await team.execute(frozen, None)
        (self.repo / "untracked.txt").write_text("mutated\n")
        out = team.finalize(
            result, ctx, self.repo,
            lead_reviewed_files=ctx["changed_files"],
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("INCOMPLETE", out["review_status"])
        self.assertIn("reviewed Git target/fingerprint changed", out["unresolved_questions"])

    async def test_missing_native_second_pass_evidence_blocks_r3(self):
        plan = self.plan(tasks=False)
        result = await team.execute(plan, None)
        bad = team.finalize(
            result, self.ctx, self.repo, lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual("INCOMPLETE", bad["review_status"])
        supported = team.finalize(
            result, self.ctx, self.repo, lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[], unresolved_material=[],
            native_second_pass_evidence=["payments.py:1"],
        )
        self.assertEqual("PASS", supported["review_status"])

    async def test_live_mode_still_relays_requests_the_audit_did_not_answer(self):
        plan = self.plan(concerns=["correctness", "reliability"], direct=True)
        host = self.host(requests=True, observe_direct=True)
        result = await team.execute(plan, host)
        self.assertEqual("team-live", result["execution_mode"])
        self.assertEqual(2, len(host.resumed))
        self.assertIn("Can two charges race?", [m.get("subject") for m in result["peer_threads"]])
        self.assertEqual([], result["unresolved_questions"])

    async def test_live_mode_keeps_a_request_the_audit_already_answered(self):
        plan = self.plan(concerns=["correctness", "reliability"], direct=True)
        host = self.host(requests=True, observe_direct=True, audit_subject="Can two charges race?")
        result = await team.execute(plan, host)
        self.assertEqual("team-live", result["execution_mode"])
        self.assertEqual([], host.resumed)
        self.assertEqual([], result["unresolved_questions"])

    async def test_finalized_evidence_lists_unreviewed_files(self):
        plan = self.plan()
        result = await team.execute(plan, self.host())
        proof = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=list(self.ctx["changed_files"]),
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual([], proof["unreviewed_files"])
        validate_evidence(proof, self.ctx, self.repo)
        partial = team.finalize(
            result, self.ctx, self.repo,
            lead_reviewed_files=["payments.py"],
            lead_independent=True, verified_blockers=[], unresolved_material=[],
        )
        self.assertEqual(
            sorted(set(self.ctx["changed_files"]) - {"payments.py"}),
            partial["unreviewed_files"],
        )

    def test_verified_readme_outside_the_diff_is_a_valid_finding_location(self):
        (self.repo / "README.md").write_text("# Payments\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-q", "-m", "docs")
        head = git(self.repo, "rev-parse", "HEAD")
        finding = {
            "finding_id": "doc-1", "location": "README.md:1",
            "claim": "The guide still describes the old amount",
            "trigger": "amount change", "evidence": "README.md:1",
            "consequence": "An operator follows a stale step",
            "severity": "medium", "confidence": "high",
        }
        team._validate_finding(finding, {"payments.py"}, repo=self.repo, head=head)

    def test_unchanged_source_file_is_not_a_documentation_location(self):
        finding = {
            "finding_id": "src-1", "location": "tests.py:1",
            "claim": "A source file outside the diff",
            "trigger": "change", "evidence": "tests.py:1",
            "consequence": "unrelated",
            "severity": "low", "confidence": "low",
        }
        with self.assertRaisesRegex(team.TeamPlanningError, "changed file"):
            team._validate_finding(finding, {"payments.py"}, repo=self.repo, head=self.head)

    async def test_readme_finding_does_not_abort_the_specialist_batch(self):
        git(self.repo, "checkout", "-q", self.base)
        (self.repo / "README.md").write_text("# Payments\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-q", "-m", "docs")
        docs = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "payments.py").write_text("amount=2\n")
        (self.repo / "tests.py").write_text("assert True\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "feature")
        head = git(self.repo, "rev-parse", "HEAD")
        ctx = prepare_context(self.repo, base=docs, head=head, allow_ocr=False)
        plan = team.freeze(
            ctx, self.repo, risk_profile="R2", concerns=["correctness", "reliability"],
            task_available=True, isolated_tasks=True, direct_peer_supported=False,
            lead_implemented_change=False, review_id="review-a",
        )
        host = self.host()
        host._repository = str(self.repo.resolve())
        host._target = dict(ctx["target"])
        original = host.task_batch
        finding = {
            "finding_id": "doc-1", "location": "README.md:1",
            "claim": "The guide still describes the old amount",
            "trigger": "amount change", "evidence": "README.md:1",
            "consequence": "An operator follows a stale step",
            "severity": "medium", "confidence": "high",
        }

        async def first_pass(requests):
            answers = await original(requests)
            if requests[0]["role"] == "finding-verifier":
                answers[0]["verified_findings"] = [{
                    "finding_id": "doc-1", "verification_status": "confirmed",
                    "location": "README.md:1",
                    "source_evidence": "README.md:1 names the old amount",
                }]
                return answers
            for answer in answers:
                if answer["role"] == "correctness-reviewer":
                    answer["candidate_findings"] = [finding]
            return answers

        host.task_batch = first_pass
        result = await team.execute(plan, host)
        self.assertEqual("README.md:1", result["raw_findings"][0]["location"])
        self.assertNotIn("README.md", result["changed_files"])


if __name__ == "__main__":
    unittest.main()
