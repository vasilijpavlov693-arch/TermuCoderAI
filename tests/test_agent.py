"""Tests for termucoder.agent (v2.0)."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAgentHistory(unittest.TestCase):

    def test_log_action(self):
        from termucoder.agent.history import log_action, get_session, new_session_id, HISTORY_DIR
        import json
        sid = new_session_id()
        # Clean up any existing file
        path = os.path.join(HISTORY_DIR, sid + ".json")
        if os.path.exists(path):
            os.remove(path)
        action = {"action": "tool_call", "tool": "read_file", "params": {"path": "test.py"}}
        log_action(sid, 1, action, "file content")
        data = get_session(sid)
        self.assertEqual(len(data["actions"]), 1)
        self.assertEqual(data["actions"][0]["step"], 1)

    def test_log_done(self):
        from termucoder.agent.history import log_action, log_done, get_session, new_session_id
        sid = new_session_id()
        log_action(sid, 1, {"action": "tool_call", "tool": "write_file"}, "ok")
        log_done(sid, "Task completed")
        data = get_session(sid)
        self.assertTrue(data["completed"])
        self.assertEqual(data["result"], "Task completed")

    def test_list_sessions(self):
        from termucoder.agent.history import log_action, list_sessions, new_session_id
        sid = new_session_id()
        log_action(sid, 1, {"action": "tool_call", "tool": "test"}, "ok")
        sessions = list_sessions()
        self.assertIn(sid, sessions)


class TestAgentCheckpoint(unittest.TestCase):

    def test_save_load_checkpoint(self):
        from termucoder.agent.checkpoint import save_checkpoint, load_checkpoint
        from termucoder.agent.history import new_session_id
        sid = new_session_id()
        history = ["[Step 1] write_file: ok"]
        save_checkpoint(sid, "test task", history, "context", 1)
        data = load_checkpoint(sid)
        self.assertEqual(data["task"], "test task")
        self.assertEqual(data["step"], 1)
        self.assertEqual(len(data["history"]), 1)

    def test_list_checkpoints(self):
        from termucoder.agent.checkpoint import save_checkpoint, list_checkpoints
        from termucoder.agent.history import new_session_id
        sid = new_session_id()
        save_checkpoint(sid, "task", [], "ctx", 0)
        cps = list_checkpoints()
        self.assertIn(sid, cps)

    def test_delete_checkpoint(self):
        from termucoder.agent.checkpoint import save_checkpoint, delete_checkpoint, load_checkpoint
        from termucoder.agent.history import new_session_id
        sid = new_session_id()
        save_checkpoint(sid, "task", [], "ctx", 0)
        self.assertTrue(delete_checkpoint(sid))
        self.assertEqual(load_checkpoint(sid), {})


class TestAgentLoop(unittest.TestCase):

    @patch("termucoder.agent.loop.LLMClient")
    def test_agent_done(self, mock_llm_class):
        from termucoder.agent.loop import run_agent
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.chat.return_value = json.dumps({
            "action": "done",
            "result": "Task completed successfully"
        })
        result = run_agent("test task", auto_approve=True)
        self.assertEqual(result, "Task completed successfully")

    @patch("termucoder.agent.loop.LLMClient")
    def test_agent_tool_call(self, mock_llm_class):
        from termucoder.agent.loop import run_agent
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.chat.side_effect = [
            json.dumps({"action": "tool_call", "tool": "list_files", "params": {"path": "."}}),
            json.dumps({"action": "done", "result": "Done listing"}),
        ]
        with tempfile.TemporaryDirectory():
            result = run_agent("list files", auto_approve=True, max_iterations=2)
        self.assertEqual(result, "Done listing")

    @patch("termucoder.agent.loop.LLMClient")
    def test_agent_limit_reached(self, mock_llm_class):
        from termucoder.agent.loop import run_agent
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.chat.return_value = json.dumps({
            "action": "tool_call", "tool": "list_files", "params": {"path": "."}
        })
        with tempfile.TemporaryDirectory():
            result = run_agent("infinite task", auto_approve=True, max_iterations=2)
        self.assertEqual(result, "Limit reached")


class TestAgentPrompts(unittest.TestCase):

    def test_system_prompt_has_tools(self):
        from termucoder.agent.prompts import SYSTEM
        self.assertIn("{tools}", SYSTEM)

    def test_task_prompt_has_placeholders(self):
        from termucoder.agent.prompts import TASK_PROMPT
        self.assertIn("{task}", TASK_PROMPT)
        self.assertIn("{context}", TASK_PROMPT)
        self.assertIn("{history}", TASK_PROMPT)


if __name__ == "__main__":
    unittest.main()
