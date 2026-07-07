"""Тесты для termucoder.api (с моком LLM-сервера)."""

import io
import json
import unittest
from unittest import mock

from termucoder.api import LLMClient


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

    def iter_lines(self, decode_unicode=True):
        for ln in self._lines:
            yield ln


class TestAPI(unittest.TestCase):

    def _patch(self, lines):
        resp = _Resp(lines)
        return mock.patch("termucoder.api.requests.post", return_value=resp)

    def test_ask(self):
        client = LLMClient()
        with self._patch(_sse(["При", "вет"])), io.StringIO() as buf:
            with mock.patch("sys.stdout", buf):
                result = client.ask("привет")
        self.assertEqual(result, "Привет")


if __name__ == "__main__":
    unittest.main()
