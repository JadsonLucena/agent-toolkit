"""Review regressions for evidence-backed refactoring assessment."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RefactoringReviewPolicyTests(unittest.TestCase):
    def test_refactoring_assessment_preserves_review_boundaries(self):
        rule = read("contexts/review/rules/code-review.md")
        self.assertIn("## Structural Refactoring Assessment", rule)
        self.assertIn("observable output", rule)
        self.assertIn("Passing tests alone are not a proof of equivalence", rule)
        self.assertIn("Review remains read-only", rule)

    def test_no_automatic_smell_blocking(self):
        rule = read("contexts/review/rules/code-review.md")
        guide = read("contexts/review/skills/review-change/references/refactoring-review.md")
        self.assertIn("A pre-existing smell or stylistic preference is normally advisory", rule)
        self.assertIn("not a blocking regression", guide)
        self.assertIn("introduced", guide)
        self.assertIn("amplified-pre-existing", guide)

    def test_reference_is_lazy_and_not_a_new_gate(self):
        skill = read("contexts/review/skills/review-change/SKILL.md")
        self.assertIn("consult `references/refactoring-review.md`", skill)
        self.assertIn("not an additional gate", skill)
        self.assertIn("Review remains read-only", read("contexts/review/rules/code-review.md"))


if __name__ == "__main__":
    unittest.main()
