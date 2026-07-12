"""Клиент LLM API для TermuCoderAI."""

import json
import requests

from termucoder.config import load_config
from termucoder.prompts import SYSTEM


class LLMClient:

    def __init__(self):

        config = load_config()

        host = config["server"]["host"]
        port = config["server"]["port"]

        self.url = f"http://{host}:{port}"

        generation = config.get(
            "generation",
            {}
        )

        self.temperature = generation.get(
            "temperature",
            0.2
        )

        self.max_tokens = generation.get(
            "max_tokens",
            512
        )

        self.top_p = generation.get(
            "top_p",
            0.9
        )

        self.top_k = generation.get(
            "top_k",
            40
        )

        self.stop = generation.get(
            "stop",
            None
        )

        self.system_prompt = config.get(
            "prompts",
            {}
        ).get(
            "system",
            SYSTEM
        )


    def _endpoint(self):

        return self.url + "/v1/chat/completions"


    def _stream(
        self,
        messages,
        temperature=None,
        max_tokens=None
    ):

        payload = {
            "messages": messages,

            "temperature":
                temperature
                if temperature is not None
                else self.temperature,

            "max_tokens":
                max_tokens
                if max_tokens is not None
                else self.max_tokens,

            "top_p": self.top_p,

            "top_k": self.top_k,

            "stop": self.stop,

            "stream": True
        }


        result = ""
        finish_reason = None


        try:

            with requests.post(
                self._endpoint(),
                json=payload,
                stream=True,
                timeout=(10, 300)
            ) as r:


                r.raise_for_status()

                r.encoding = "utf-8"


                for line in r.iter_lines(
                    decode_unicode=True
                ):

                    if not line:
                        continue


                    if not line.startswith("data:"):
                        continue


                    data = line[5:].strip()


                    if data == "[DONE]":
                        break


                    try:
                        obj = json.loads(data)

                    except Exception:
                        continue


                    choice = obj.get(
                        "choices",
                        [{}]
                    )[0]


                    delta = choice.get(
                        "delta",
                        {}
                    )


                    text = delta.get(
                        "content",
                        ""
                    )


                    if text:

                        print(
                            text,
                            end="",
                            flush=True
                        )

                        result += text


                    if choice.get(
                        "finish_reason"
                    ):

                        finish_reason = choice["finish_reason"]
                        break



        except requests.exceptions.ConnectionError:

            print("\n❌ AI сервер недоступен")


        except requests.exceptions.Timeout:

            print("\n❌ Таймаут генерации")


        except Exception as e:

            print(
                f"\n❌ Ошибка: {e}"
            )


        if finish_reason == "length":

            print(
                "\n\n[!] Ответ достиг лимита токенов"
            )


        print()

        return result



    def ask(self, prompt):

        messages = [

            {
                "role": "system",
                "content": self.system_prompt
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

        return self._stream(messages)



    def chat(self, history):

        messages = [

            {
                "role": "system",
                "content": self.system_prompt
            }

        ]

        messages.extend(history)

        return self._stream(messages)



    def ask_context(
        self,
        context,
        question
    ):

        messages = [

            {
                "role": "system",
                "content": self.system_prompt
            },

            {
                "role": "user",
                "content":
                    f"Контекст проекта:\n\n{context}\n\n"
                    f"Вопрос:\n{question}"
            }

        ]


        return self._stream(messages)
