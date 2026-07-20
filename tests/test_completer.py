"""Тесты для termucoder.completer (v0.8)."""

import unittest

from termucoder.completer import (
    COMMANDS, SUBCOMMANDS, FLAGS, GLOBAL_FLAGS,
    TermuCompleter, _get_command, _complete_path,
)
from termucoder.utils import (
    ok, success, error, warning, note, header, muted,
    bold, dim, code, info, separator, table,
)


class TestCompleter(unittest.TestCase):

    def test_commands_list(self):
        self.assertIn("ask", COMMANDS)
        self.assertIn("chat", COMMANDS)
        self.assertIn("edit", COMMANDS)
        self.assertIn("memory", COMMANDS)
        self.assertIn("plugin", COMMANDS)
        self.assertIn("config", COMMANDS)
        self.assertIn("server", COMMANDS)
        self.assertIn("model", COMMANDS)

    def test_subcommands(self):
        self.assertIn("start", SUBCOMMANDS["server"])
        self.assertIn("stop", SUBCOMMANDS["server"])
        self.assertIn("list", SUBCOMMANDS["model"])
        self.assertIn("add", SUBCOMMANDS["memory"])

    def test_flags(self):
        self.assertIn("--preview", FLAGS["edit"])
        self.assertIn("--undo", FLAGS["edit"])
        self.assertIn("--new", FLAGS["chat"])
        self.assertIn("--list", FLAGS["chat"])

    def test_get_command(self):
        self.assertEqual(_get_command(["ask", "hello"]), "ask")
        self.assertEqual(_get_command(["server", "start"]), "server")
        self.assertEqual(_get_command(["--help"]), None)
        self.assertEqual(_get_command([]), None)

    def test_complete_path(self):
        matches = _complete_path("termucoder/")
        self.assertIn("cli.py", matches)
        self.assertIn("api.py", matches)

    def test_complete_path_empty(self):
        matches = _complete_path("")
        self.assertIsInstance(matches, list)


class TestColorHelpers(unittest.TestCase):

    def test_ok(self):
        result = ok("test")
        self.assertIn("test", result)

    def test_error(self):
        result = error("test")
        self.assertIn("test", result)

    def test_warning(self):
        result = warning("test")
        self.assertIn("test", result)

    def test_header(self):
        result = header("test")
        self.assertIn("test", result)

    def test_bold(self):
        result = bold("test")
        self.assertIn("test", result)

    def test_dim(self):
        result = dim("test")
        self.assertIn("test", result)

    def test_code(self):
        result = code("test")
        self.assertIn("test", result)

    def test_success(self):
        result = success("test")
        self.assertIn("test", result)

    def test_info(self):
        result = info("test")
        self.assertIn("test", result)

    def test_separator(self):
        result = separator()
        self.assertIn("─", result)

    def test_table(self):
        result = table(["Name", "Value"], [["a", "1"], ["b", "2"]])
        self.assertIn("Name", result)
        self.assertIn("Value", result)
        self.assertIn("a", result)
        self.assertIn("2", result)

    def test_table_empty(self):
        result = table(["Name"], [])
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
