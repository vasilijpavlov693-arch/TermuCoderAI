"""Тесты для termucoder.editor и termucoder.search_replace."""

import os
import tempfile
import unittest

from termucoder.edit_validator import is_valid
from termucoder.search_replace import parse_blocks, apply_changes, ReplaceError, clean_replace


class TestEditValidator(unittest.TestCase):

    def test_valid_block(self):
        response = (
            "SEARCH\n"
            "def main():\n"
            "    pass\n"
            "REPLACE\n"
            "def main():\n"
            "    print('hello')\n"
            "END"
        )
        self.assertTrue(is_valid(response))

    def test_no_search(self):
        self.assertFalse(is_valid("REPLACE\nx\nEND"))

    def test_no_replace(self):
        self.assertFalse(is_valid("SEARCH\nx\nEND"))

    def test_markdown_response(self):
        response = (
            "```python\n"
            "SEARCH\nold\nREPLACE\nnew\nEND\n"
            "```"
        )
        self.assertFalse(is_valid(response))

    def test_too_long(self):
        response = "SEARCH\n" + "x" * 6000 + "\nREPLACE\ny\nEND"
        self.assertFalse(is_valid(response))

    def test_empty_search(self):
        self.assertFalse(is_valid("SEARCH\n\nREPLACE\nnew\nEND"))

    def test_empty_replace(self):
        self.assertFalse(is_valid("SEARCH\nold\nREPLACE\n\nEND"))

    def test_search_equals_replace(self):
        self.assertFalse(is_valid("SEARCH\nsame\nREPLACE\nsame\nEND"))

    def test_single_word_search(self):
        self.assertFalse(is_valid("SEARCH\nhello\nREPLACE\nworld\nEND"))

    def test_replace_too_large(self):
        search = "short"
        replace = "x" * 101
        self.assertFalse(is_valid(f"SEARCH\n{search}\nREPLACE\n{replace}\nEND"))


class TestSearchReplace(unittest.TestCase):

    def test_clean_replace_strips_end(self):
        text = "new code\nEND"
        self.assertEqual(clean_replace(text), "new code")

    def test_clean_replace_strips_marker(self):
        text = "new code\n===== КОНЕЦ =====\nother"
        self.assertEqual(clean_replace(text), "new code")

    def test_parse_blocks_basic(self):
        response = (
            "SEARCH\nold text\nREPLACE\nnew text\nEND"
        )
        blocks = parse_blocks(response)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0], ("old text", "new text"))

    def test_parse_blocks_skips_identical(self):
        response = (
            "SEARCH\nsame\nREPLACE\nsame\nEND"
        )
        blocks = parse_blocks(response)
        self.assertEqual(len(blocks), 0)

    def test_parse_blocks_skips_empty(self):
        response = (
            "SEARCH\n\nREPLACE\nnew\nEND"
        )
        blocks = parse_blocks(response)
        self.assertEqual(len(blocks), 0)

    def test_apply_changes_success(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("def main():\n    pass\n")
            path = f.name

        try:
            response = (
                "SEARCH\n"
                "    pass\n"
                "REPLACE\n"
                "    print('hello')\n"
                "END"
            )
            result = apply_changes(path, response)
            self.assertTrue(result["changed"])
            self.assertEqual(result["blocks"], 1)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("print('hello')", content)
            self.assertNotIn("pass", content)
        finally:
            os.unlink(path)

    def test_apply_changes_file_not_found(self):
        with self.assertRaises(ReplaceError):
            apply_changes("/nonexistent/file.py", "SEARCH\na\nREPLACE\nb\nEND")

    def test_apply_changes_no_blocks(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("hello")
            path = f.name

        try:
            with self.assertRaises(ReplaceError):
                apply_changes(path, "no search replace here")
        finally:
            os.unlink(path)

    def test_apply_changes_search_not_found(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("hello world")
            path = f.name

        try:
            with self.assertRaises(ReplaceError):
                apply_changes(path, "SEARCH\nnonexistent\nREPLACE\nnew\nEND")
        finally:
            os.unlink(path)

    def test_apply_changes_search_multiple_matches(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("aaa\nbbb\naaa")
            path = f.name

        try:
            with self.assertRaises(ReplaceError):
                apply_changes(path, "SEARCH\naaa\nREPLACE\nccc\nEND")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
