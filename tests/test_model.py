"""Tests for termucoder.model."""
import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestModel(unittest.TestCase):

    @patch("termucoder.model.load_config")
    def test_info_model(self, mock_cfg):
        mock_cfg.return_value = {"model": {"name": "test.gguf", "path": "/fake/model.gguf"}}
        from termucoder.model import info_model
        with patch("builtins.print"):
            info_model()

    @patch("termucoder.model.load_config")
    @patch("os.listdir", return_value=["model1.gguf", "model2.gguf"])
    @patch("os.path.isdir", return_value=True)
    def test_list_models(self, mock_isdir, mock_listdir, mock_cfg):
        mock_cfg.return_value = {"model": {"name": "model1.gguf"}}
        from termucoder.model import list_models
        with patch("builtins.print"):
            list_models()


if __name__ == "__main__":
    unittest.main()
