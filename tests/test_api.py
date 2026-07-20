"""Тесты для termucoder.api (с моком LLM-сервера)."""

import importlib.util
import io
import json
import unittest
from unittest import mock

from termucoder.api import LLMClient


_HAS_REQUESTS = importlib.util.find_spec("requests") is not None


def _sse(lines):
    """Формирует поток SSE-строк, как у llama-server."""
    out = []
    for text in lines:
        chunk = {
            "choices": [{
                "delta": {"content": text}
            }]
        }
        out.append("data: " + json.dumps(chunk))
    out.append("data: [DONE]")
    return out


class _Resp:
    def __init__(self, lines):
        self._lines = lines
        self.encoding = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def raise_for_status(self):
        pass

    def iter_lines(self, decode_unicode=True):
        for ln in self._lines:
            yield ln


@unittest.skipUnless(_HAS_REQUESTS, "требуется пакет requests")
class TestAPI(unittest.TestCase):

    def _patch(self, lines):
        resp = _Resp(lines)
        return mock.patch("termucoder.api.requests.post", return_value=resp)

    def test_ask(self):
        client = LLMClient()
        with self._patch(_sse(["При", "вет"])), io.StringIO() as buf:
            # Перехватываем stdout, чтобы не засорять вывод.
            with mock.patch("sys.stdout", buf):
                result = client.ask("привет")
        self.assertEqual(result, "Привет")

    def test_chat_keeps_history(self):
        client = LLMClient()
        history = [
            {"role": "user", "content": "кто ты?"},
            {"role": "assistant", "content": "я бот"},
        ]
        with self._patch(_sse(["ок"])), io.StringIO() as buf:
            with mock.patch("sys.stdout", buf):
                result = client.chat(history)
        self.assertEqual(result, "ок")

    def test_ask_context(self):
        client = LLMClient()
        with self._patch(_sse(["анализ"])), io.StringIO() as buf:
            with mock.patch("sys.stdout", buf):
                result = client.ask_context("контекст", "вопрос")
        self.assertEqual(result, "анализ")


if __name__ == "__main__":
    unittest.main()
