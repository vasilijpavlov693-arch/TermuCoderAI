"""Tests for termucoder.tokens."""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCountTokens(unittest.TestCase):

    def test_empty(self):
        from termucoder.tokens import count_tokens
        self.assertEqual(count_tokens(""), 0)
        self.assertEqual(count_tokens(None), 0)

    def test_latin(self):
        from termucoder.tokens import count_tokens
        result = count_tokens("hello world")
        self.assertGreater(result, 0)
        self.assertLess(result, 10)

    def test_cyrillic(self):
        from termucoder.tokens import count_tokens
        result = count_tokens("привет мир")
        self.assertGreater(result, 0)

    def test_long_text(self):
        from termucoder.tokens import count_tokens
        text = "word " * 1000
        result = count_tokens(text)
        self.assertGreater(result, 100)


class TestFitMessages(unittest.TestCase):

    def test_fits_all(self):
        from termucoder.tokens import fit_messages_to_context
        msgs = [{"role": "user", "content": "hi"}]
        result = fit_messages_to_context(msgs, context_size=4096)
        self.assertEqual(len(result), 1)

    def test_trims_old(self):
        from termucoder.tokens import fit_messages_to_context
        msgs = [{"role": "user", "content": "word " * 200} for i in range(20)]
        result = fit_messages_to_context(msgs, context_size=500, max_response=100)
        self.assertLess(len(result), 20)

    def test_keeps_at_least_one(self):
        from termucoder.tokens import fit_messages_to_context
        msgs = [{"role": "user", "content": "x" * 10000}]
        result = fit_messages_to_context(msgs, context_size=100)
        self.assertEqual(len(result), 1)


class TestSummarizeMessages(unittest.TestCase):

    def test_short_unchanged(self):
        from termucoder.tokens import summarize_messages
        msgs = [{"role": "user", "content": "hi"}]
        result = summarize_messages(msgs, keep_recent=4)
        self.assertEqual(len(result), 1)

    def test_long_summarized(self):
        from termucoder.tokens import summarize_messages
        msgs = [{"role": "user", "content": "msg " + str(i)} for i in range(10)]
        result = summarize_messages(msgs, keep_recent=4)
        self.assertLess(len(result), 10)
        self.assertIn("system", result[0].get("role", ""))


if __name__ == "__main__":
    unittest.main()
