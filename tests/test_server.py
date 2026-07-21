"""Tests for termucoder.server (cross-platform)."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestServer(unittest.TestCase):

    @patch("termucoder.server._find_llama_server")
    @patch("termucoder.server.load_config")
    def test_get_command_raises_no_model(self, mock_cfg, mock_find):
        mock_find.return_value = "/fake/llama-server"
        mock_cfg.return_value = {"server": {}, "model": {"path": ""}}
        from termucoder.server import get_command
        with self.assertRaises(Exception) as ctx:
            get_command()
        self.assertIn("не указан", str(ctx.exception))

    @patch("termucoder.server._find_llama_server")
    @patch("termucoder.server.load_config")
    def test_get_command_raises_missing_model(self, mock_cfg, mock_find):
        mock_find.return_value = "/fake/llama-server"
        mock_cfg.return_value = {"server": {}, "model": {"path": "/nonexistent/model.gguf"}}
        from termucoder.server import get_command
        with self.assertRaises(Exception) as ctx:
            get_command()
        self.assertIn("не найдена", str(ctx.exception))

    @patch("termucoder.server._find_llama_server")
    @patch("termucoder.server.load_config")
    def test_get_command_no_binary(self, mock_cfg, mock_find):
        mock_find.return_value = None
        mock_cfg.return_value = {"server": {}, "model": {"path": "/fake/model.gguf"}}
        from termucoder.server import get_command
        with self.assertRaises(Exception) as ctx:
            get_command()
        self.assertIn("не найден", str(ctx.exception))

    @patch("termucoder.server._pid_exists", return_value=False)
    @patch("termucoder.server.get_saved_pid", return_value=None)
    @patch("termucoder.server.find_existing_server", return_value=None)
    def test_is_running_false(self, mock_find, mock_saved, mock_exists):
        from termucoder.server import is_running
        self.assertFalse(is_running())

    @patch("termucoder.server.get_saved_pid", return_value=99999)
    @patch("termucoder.server._pid_exists", return_value=False)
    @patch("termucoder.server.find_existing_server", return_value=None)
    def test_is_running_pid_dead(self, mock_find, mock_exists, mock_saved):
        from termucoder.server import is_running
        self.assertFalse(is_running())

    @patch("termucoder.server._pid_exists", return_value=False)
    @patch("termucoder.server.get_saved_pid", return_value=None)
    @patch("termucoder.server.find_existing_server", return_value=None)
    def test_get_running_pid_none(self, mock_find, mock_saved, mock_exists):
        from termucoder.server import get_running_pid
        self.assertIsNone(get_running_pid())


class TestFindLlamaServer(unittest.TestCase):

    @patch("shutil.which", return_value=None)
    @patch("os.path.isfile", return_value=False)
    def test_not_found(self, mock_isfile, mock_which):
        from termucoder.server import _find_llama_server
        result = _find_llama_server()
        self.assertIsNone(result)

    @patch("shutil.which", return_value="/usr/bin/llama-server")
    @patch("os.path.isfile", return_value=False)
    def test_found_in_path(self, mock_isfile, mock_which):
        from termucoder.server import _find_llama_server
        result = _find_llama_server()
        self.assertEqual(result, "/usr/bin/llama-server")


if __name__ == "__main__":
    unittest.main()
