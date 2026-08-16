import json
import unittest
from pathlib import Path

from jobextractor import SelectorConfig, extract_jobs


ROOT = Path(__file__).resolve().parents[1]


class ExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = (ROOT / "tests" / "fixtures" / "jobs.html").read_text(encoding="utf-8")
        self.config = SelectorConfig(**json.loads((ROOT / "examples" / "selectors.json").read_text(encoding="utf-8")))

    def test_extracts_normalized_unique_jobs(self) -> None:
        result = extract_jobs(self.html, "https://jobs.example.test", self.config)
        self.assertEqual(2, len(result.jobs))
        self.assertEqual("https://jobs.example.test/jobs/42", result.jobs[0].url)
        self.assertEqual("https://apply.example.test/qa", result.jobs[1].url)

    def test_reports_duplicate_and_incomplete_cards(self) -> None:
        result = extract_jobs(self.html, "https://jobs.example.test", self.config)
        self.assertEqual(2, len(result.warnings))
        self.assertIn("duplicate", result.warnings[0])
        self.assertIn("missing", result.warnings[1])

    def test_rejects_complex_selectors(self) -> None:
        with self.assertRaises(ValueError):
            extract_jobs(self.html, "https://jobs.example.test", SelectorConfig("article > div", ".title", ".company", ".location", "a"))


if __name__ == "__main__":
    unittest.main()
