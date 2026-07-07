"""Тесты для termucoder.context (v0.4)."""

import os
import tempfile
import unittest

from termucoder import context


class TestContext(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

        self._make({
            "README.md": "# Demo\nОписание проекта.",
            "main.py": "def main():\n    pass\n",
            "sub/util.py": "def helper():\n    return 1\n",
        })

    def tearDown(self):
        os.chdir(self._orig)

    def _make(self, tree):
        for name, content in tree.items():
            path = os.path.join(self._tmp, name)
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def test_build_structure(self):
        info = context.analyze_project(".")
        struct = info["structure"]
        self.assertIn("README.md", struct)
        self.assertIn("main.py", struct)
        self.assertIn("sub", struct)

    def test_read_docs(self):
        info = context.analyze_project(".")
        self.assertIn("Описание проекта", info["docs"])

    def test_contents(self):
        info = context.analyze_project(".")
        self.assertIn("main.py", info["contents"])
        self.assertIn("def main", info["contents"]["main.py"])

    def test_summarize(self):
        out = context.summarize(".")
        self.assertIn("Файлов всего", out)
        self.assertIn("main.py", out)

    def test_build_prompt(self):
        prompt = context.build_prompt(".")
        self.assertIn("Структура проекта", prompt)
        self.assertIn("def main", prompt)


if __name__ == "__main__":
    unittest.main()
