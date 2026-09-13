"""Offline regression checks for source citations and containment."""
from pathlib import Path
import copy
import importlib.util
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("source_evidence", Path(__file__).with_name("source_evidence.py"))
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "main.py").write_text("def greet():\n    return 'hello'\n", encoding="utf-8")

    def snapshot(self):
        return evidence.capture(self.root, ["main.py:1:2"])

    def test_exact_excerpt_and_relative_path(self):
        doc = self.snapshot()
        self.assertEqual(doc["sources"][0]["path"], "main.py")
        self.assertEqual(doc["sources"][0]["excerpt"], "def greet():\n    return 'hello'")
        self.assertEqual(evidence.verify(self.root, doc)[0]["status"], "verified")

    def test_changed_file_detected_outside_excerpt(self):
        doc = evidence.capture(self.root, ["main.py:1:1"])
        (self.root / "main.py").write_text("def greet():\n    return 'changed'\n", encoding="utf-8")
        self.assertEqual(evidence.verify(self.root, doc)[0]["status"], "changed")

    def test_tampered_excerpt_detected(self):
        doc = self.snapshot()
        doc["sources"][0]["excerpt"] = "invented claim"
        self.assertEqual(evidence.verify(self.root, doc)[0]["status"], "excerpt_mismatch")

    def test_missing_file_reported(self):
        doc = self.snapshot()
        (self.root / "main.py").unlink()
        self.assertEqual(evidence.verify(self.root, doc)[0]["status"], "missing")

    def test_traversal_and_absolute_paths_rejected(self):
        for name in ["../outside.py", str(self.root / "main.py"), "C:/private.py"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                evidence.capture(self.root, [name + ":1:1"])

    def test_common_credentials_rejected(self):
        for name in [".env", ".env.local", "credentials.json", "secret.key", ".git/config"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                evidence.capture(self.root, [name + ":1:1"])

    def test_invalid_range_rejected(self):
        for ref in ["main.py:0:1", "main.py:2:1", "main.py:1:99", "main.py"]:
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                evidence.capture(self.root, [ref])

    def test_binary_rejected(self):
        (self.root / "binary.txt").write_bytes(b"abc\x00def")
        with self.assertRaises(ValueError):
            evidence.capture(self.root, ["binary.txt:1:1"])

    def test_relocated_repository_path(self):
        doc = self.snapshot()
        with tempfile.TemporaryDirectory() as folder:
            moved = Path(folder)
            (moved / "main.py").write_bytes((self.root / "main.py").read_bytes())
            self.assertEqual(evidence.verify(moved, doc)[0]["status"], "verified")

    def test_malformed_manifest_fails_closed(self):
        with self.assertRaises(ValueError):
            evidence.verify(self.root, [])
        doc = self.snapshot()
        doc["sources"] = ["invalid"]
        self.assertEqual(evidence.verify(self.root, doc)[0]["status"], "blocked_or_invalid")

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "outside.py"
            target.write_text("private = True", encoding="utf-8")
            link = self.root / "link.py"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("This platform requires additional privilege for symlinks")
            with self.assertRaises(ValueError):
                evidence.capture(self.root, ["link.py:1:1"])


if __name__ == "__main__":
    unittest.main()
