"""Тесты для termucoder.search (v0.4)."""

import os
import tempfile
import unittest

from termucoder import search
from termucoder.utils import read_gitignore, is_ignored


class TestSearch(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig)

    def _make(self, tree):
        for name, content in tree.items():
            path = os.path.join(self._tmp, name)
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(name) else None
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def test_ignored_dirs_skipped(self):
        self._make({
            "main.py": "x",
            "__pycache__/cache.py": "y",
            ".git/config": "z",
            "sub/module.py": "w",
        })
        files = search.scan_project(".")
        self.assertIn("main.py", files)
        self.assertIn("sub/module.py", files)
        self.assertNotIn("__pycache__/cache.py", files)
        self.assertNotIn(".git/config", files)

    def test_gitignore(self):
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write("secret.txt\n*.log\n")

        self._make({
            "app.py": "x",
            "secret.txt": "y",
            "debug.log": "z",
        })
        files = search.scan_project(".")
        self.assertIn("app.py", files)
        self.assertNotIn("secret.txt", files)
        self.assertNotIn("debug.log", files)

    def test_read_gitignore_empty(self):
        self.assertEqual(read_gitignore("."), set())

    def test_is_ignored(self):
        patterns = {"*.pyc", "build", "foo.txt"}
        self.assertTrue(is_ignored("a.pyc", patterns))
        self.assertTrue(is_ignored("build/x.txt", patterns))
        self.assertTrue(is_ignored("foo.txt", patterns))
        self.assertFalse(is_ignored("main.py", patterns))


if __name__ == "__main__":
    unittest.main()
