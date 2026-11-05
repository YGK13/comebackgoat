"""The participant kit ships the right skills, fills coach links and never ships the coach skill."""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_kit", ROOT / "scripts/build_kit.py")
bk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bk)


class BuildKitTests(unittest.TestCase):
    def test_kit_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = bk.build(draft=True, out=Path(tmp) / "dist")
            with zipfile.ZipFile(r["kit"]) as z:
                names = z.namelist()
                self.assertIn("comeback-goat-kit/CLAUDE-SETUP.md", names)
                self.assertIn("comeback-goat-kit/PARTICIPANT-PROTOCOL.md", names)
                for s in bk.REQUIRED_SKILLS:
                    self.assertIn(f"comeback-goat-kit/skills/{s}.zip", names)
                self.assertFalse(any("cohort-operator" in n for n in names))
                self.assertFalse(any("__pycache__" in n for n in names))
            skill = Path(tmp) / "dist/comeback-goat-kit/skills/daily-plan.zip"
            with zipfile.ZipFile(skill) as z:
                self.assertIn("daily-plan/SKILL.md", z.namelist())

    def test_links_are_filled(self):
        vals = {"BOOKING_URL": "https://calendly.com/x", "WHATSAPP_GROUP_LINK": "https://chat.whatsapp.com/A",
                "WHATSAPP_DM_LINK": "https://wa.me/1", "COACH_NAME": "Yuri"}
        text = bk.fill((ROOT / "program/PARTICIPANT-PROTOCOL.md").read_text(), vals)
        self.assertIn("https://chat.whatsapp.com/A", text)
        self.assertNotIn("{{WHATSAPP", text)


if __name__ == "__main__":
    unittest.main()
