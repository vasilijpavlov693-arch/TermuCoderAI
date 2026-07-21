"""Tests for termucoder.doctor."""
import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDoctor(unittest.TestCase):

    @patch("termucoder.doctor._find_llama_server")
    @patch("termucoder.doctor.load_config")
    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1024*1024*500)
    def test_doctor_all_ok(self, mock_getsize, mock_exists, mock_cfg, mock_find):
        mock_find.return_value = "/fake/llama-server"
        mock_cfg.return_value = {
            "model": {"path": "/fake/model.gguf", "name": "test.gguf"},
            "server": {"host": "127.0.0.1", "port": 8080}
        }
        from termucoder.doctor import doctor
        with patch("builtins.print"):
            result = doctor()
        self.assertTrue(result)

    @patch("termucoder.doctor._find_llama_server", return_value=None)
    @patch("termucoder.doctor.load_config")
    @patch("os.path.exists", return_value=True)
    def test_doctor_no_server(self, mock_exists, mock_cfg, mock_find):
        mock_cfg.return_value = {"model": {"path": "", "name": "test.gguf"}, "server": {}}
        from termucoder.doctor import doctor
        with patch("builtins.print"):
            result = doctor()
        self.assertFalse(result)

    @patch("termucoder.doctor._find_llama_server")
    @patch("termucoder.doctor.load_config")
    @patch("os.path.exists")
    def test_doctor_no_model(self, mock_exists, mock_cfg, mock_find):
        mock_find.return_value = "/fake/llama-server"
        mock_cfg.return_value = {
            "model": {"path": "/nonexistent/model.gguf", "name": "test.gguf"},
            "server": {"host": "127.0.0.1", "port": 8080}
        }
        mock_exists.side_effect = lambda p: "settings" in p or "llama" in p
        from termucoder.doctor import doctor
        with patch("builtins.print"):
            result = doctor()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
