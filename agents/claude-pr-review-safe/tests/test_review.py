import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from claude_review.review import (
    REVIEW_SCHEMA,
    ReviewError,
    extract_structured_output,
    render_markdown,
    run_claude_review,
    validate_review,
)


VALID_REVIEW = {
    "summary": [
        "Adds a CLI around Claude Code.",
        "The command prints a structured review.",
    ],
    "risks": [
        {
            "severity": "Medium",
            "finding": "A large diff could be sent without a size bound.",
            "location": "src/review.py:42",
        }
    ],
    "suggestions": ["Reject oversized diffs before invoking Claude Code."],
    "confidence": "Medium",
}


class StructuredReviewTests(unittest.TestCase):
    def test_extracts_structured_output_from_cli_json(self):
        response = json.dumps(
            {"structured_output": VALID_REVIEW, "total_cost_usd": 0.01}
        )
        self.assertEqual(extract_structured_output(response).as_dict(), VALID_REVIEW)

    def test_extracts_json_encoded_result_for_older_cli_versions(self):
        response = json.dumps({"result": json.dumps(VALID_REVIEW)})
        self.assertEqual(extract_structured_output(response).as_dict(), VALID_REVIEW)

    def test_rejects_invalid_contract(self):
        invalid = dict(VALID_REVIEW, confidence="Certain")
        with self.assertRaisesRegex(ReviewError, "Confidence"):
            validate_review(invalid)
        invalid = dict(VALID_REVIEW, extra="not allowed")
        with self.assertRaisesRegex(ReviewError, "unexpected"):
            validate_review(invalid)
        invalid = dict(VALID_REVIEW, summary=["Only one sentence."])
        with self.assertRaisesRegex(ReviewError, "two or three"):
            validate_review(invalid)

    def test_markdown_contains_required_sections_and_safe_empty_states(self):
        review = validate_review(
            {
                "summary": VALID_REVIEW["summary"],
                "risks": [],
                "suggestions": [],
                "confidence": "High",
            }
        )
        markdown = render_markdown("https://github.com/example/repo/pull/4", review)
        self.assertIn("### Summary", markdown)
        self.assertIn("### Risks\n- No concrete risks", markdown)
        self.assertIn("### Improvement suggestions\n- None", markdown)
        self.assertIn("**Confidence:** High", markdown)

    def test_neutralizes_mentions_before_markdown_can_be_posted(self):
        review = validate_review(
            {
                "summary": ["Changed @owner code safely.", "The diff is small."],
                "risks": [],
                "suggestions": ["Ask @maintainer to add a regression test."],
                "confidence": "Medium",
            }
        )
        markdown = render_markdown("https://github.com/example/repo/pull/4", review)
        self.assertNotIn("@owner", markdown)
        self.assertNotIn("@maintainer", markdown)


class ClaudeInvocationTests(unittest.TestCase):
    def test_invokes_cli_without_tools_in_temporary_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / "claude"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, sys\n"
                "assert sys.argv[1] == '-p'\n"
                "assert sys.argv[sys.argv.index('--tools') + 1] == ''\n"
                "assert '--no-session-persistence' in sys.argv\n"
                "assert '--strict-mcp-config' in sys.argv\n"
                "assert os.path.basename(os.getcwd()).startswith('claude-pr-review-')\n"
                f"print(json.dumps({{'structured_output': {json.dumps(VALID_REVIEW)}}}))\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            with patch.dict(
                os.environ, {"HOME": folder, "PATH": os.environ.get("PATH", "")}
            ):
                review = run_claude_review(
                    "diff text",
                    "https://github.com/example/repo/pull/4",
                    claude_bin=str(fake),
                )
        self.assertEqual(review.as_dict(), VALID_REVIEW)

    def test_budget_is_bounded(self):
        with self.assertRaisesRegex(ReviewError, "Budget"):
            run_claude_review("diff", "local diff", budget_usd=20.01)

    def test_schema_requires_exact_contract(self):
        self.assertFalse(REVIEW_SCHEMA["additionalProperties"])
        self.assertEqual(
            set(REVIEW_SCHEMA["required"]),
            {"summary", "risks", "suggestions", "confidence"},
        )


if __name__ == "__main__":
    unittest.main()
