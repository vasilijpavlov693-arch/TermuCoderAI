"""Клиент LLM API для TermuCoderAI.

Обёртка над llama-server (совместимый с OpenAI API эндпоинт
``/v1/chat/completions``). Поддерживает потоковую генерацию, диалог с
историей сообщений и отправку контекста проекта.
"""

import json
import requests

from termucoder.config import load_config
from termucoder.prompts import SYSTEM


class LLMClient:
    """Клиент локального LLM-сервера."""

    def __init__(self):
        config = load_config()

        host = config["server"]["host"]
        port = config["server"]["port"]

        self.url = f"http://{host}:{port}"
        self.temperature = config["generation"]["temperature"]
        self.max_tokens = config["generation"]["max_tokens"]
        self.system_prompt = config.get("prompts", {}).get("system", SYSTEM)

    # ------------------------------------------------------------------
    # Внутренние хелперы
    # ------------------------------------------------------------------

    def _endpoint(self) -> str:
        return self.url + "/v1/chat/completions"

    def _stream(self, messages, temperature=None, max_tokens=None):
        """Отправляет запрос и потоково выводит ответ. Возвращает весь текст."""
        payload = {
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            "stream": True
        }

        result = ""

        try:
            with requests.post(
                self._endpoint(),
                json=payload,
                stream=True,
                timeout=300
            ) as r:
                r.encoding = "utf-8"

                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    if not line.startswith("data: "):
                        continue

                    data = line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    text = obj["choices"][0]["delta"].get("content", "")

                    if text:
                        print(text, end="", flush=True)
                        result += text

        except requests.exceptions.ConnectionError:
            print("\n❌ AI сервер недоступен")
        except requests.exceptions.Timeout:
            print("\n❌ Превышено время ожидания ответа")
        except Exception as exc:  # noqa: BLE001
            print(f"\n❌ Ошибка запроса: {exc}")

        return result

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

    def ask(self, prompt: str) -> str:
        """Отправляет одиночный вопрос без истории."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        print()
        return self._stream(messages)

    def chat(self, history) -> str:
        """Проводит диалог с моделью, передавая полную историю сообщений.

        ``history`` — список словарей {"role": ..., "content": ...}
        (только сообщения user/assistant, system добавляется автоматически).
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)

        print()
        return self._stream(messages)

    def ask_context(self, context: str, question: str) -> str:
        """Отправляет вопрос вместе с контекстом проекта."""
        user_content = (
            "Вот информация о проекте:\n\n"
            f"{context}\n\n"
            "--- КОНЕЦ КОНТЕКСТА ---\n\n"
            f"Вопрос: {question}"
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]

        print()
        return self._stream(messages)
