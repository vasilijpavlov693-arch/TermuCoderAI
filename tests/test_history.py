"""Тесты для termucoder.history (v0.3)."""

import os
import tempfile
import unittest

from termucoder import history


class TestHistory(unittest.TestCase):

    def setUp(self):
        self._orig = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig)

    def test_save_and_load(self):
        sid = "sess1"
        messages = [
            {"role": "user", "content": "привет"},
            {"role": "assistant", "content": "привет!"},
        ]
        history.save_session(sid, messages)
        self.assertEqual(history.load_session(sid), messages)

    def test_load_missing(self):
        self.assertEqual(history.load_session("nope"), [])

    def test_list_and_latest(self):
        history.save_session("a", [])
        history.save_session("b", [])
        sessions = history.list_sessions()
        self.assertIn("a", sessions)
        self.assertIn("b", sessions)
        self.assertEqual(history.latest_session(), "b")

    def test_delete(self):
        history.save_session("x", [])
        self.assertTrue(history.delete_session("x"))
        self.assertFalse(history.delete_session("x"))


if __name__ == "__main__":
    unittest.main()
