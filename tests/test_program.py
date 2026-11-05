"""The sprint skill must ship the same protocol participants load. Run: python3 -m unittest discover tests"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProgramTests(unittest.TestCase):
    def test_skill_protocol_matches_program_protocol(self):
        a = (ROOT / "program/PARTICIPANT-PROTOCOL.md").read_text(encoding="utf-8")
        b = (ROOT / "skills/comeback-sprint/references/protocol.md").read_text(encoding="utf-8")
        self.assertEqual(a, b, "copy program/PARTICIPANT-PROTOCOL.md to skills/comeback-sprint/references/protocol.md")

    def test_protocol_keeps_draft_only_rule(self):
        t = (ROOT / "program/PARTICIPANT-PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("**Draft only.**", t)
        self.assertIn("never send, submit, post", t)

    def test_no_em_dashes_in_program(self):
        for p in (ROOT / "program").glob("*.md"):
            self.assertNotIn("—", p.read_text(encoding="utf-8"), p.name)


if __name__ == "__main__":
    unittest.main()
