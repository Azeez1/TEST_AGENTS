"""Offline checks for bundling, missing markers, and overwrite protection."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("eli5_builder", Path(__file__).with_name("build.py"))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildTests(unittest.TestCase):
    def test_complete_portable_example(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "lesson.html"
            builder.build(builder.SKILL_ROOT / "assets/cache-lab.html", output)
            text = output.read_text(encoding="utf-8")
            self.assertNotIn("<!-- ELI5:", text)
            self.assertIn("<style>", text)
            self.assertIn("data-prediction", text)
            self.assertNotRegex(text, r'<(?:script|link|img)[^>]+(?:src|href)=["\x27]https?://')

    def test_existing_output_is_preserved_without_force(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "lesson.html"
            output.write_text("user content", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                builder.build(builder.SKILL_ROOT / "assets/cache-lab.html", output)
            self.assertEqual(output.read_text(encoding="utf-8"), "user content")

    def test_missing_marker_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source.html", Path(folder) / "out.html"
            source.write_text("<html>incomplete source</html>", encoding="utf-8")
            with self.assertRaises(ValueError):
                builder.build(source, output)
            self.assertFalse(output.exists())

    def test_source_cannot_be_overwritten_even_with_force(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.html"
            source.write_text("original", encoding="utf-8")
            with self.assertRaises(ValueError):
                builder.build(source, source, force=True)
            self.assertEqual(source.read_text(encoding="utf-8"), "original")

    def test_explicit_force_replaces_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "lesson.html"
            output.write_text("old lesson", encoding="utf-8")
            builder.build(builder.SKILL_ROOT / "assets/cache-lab.html", output, force=True)
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
