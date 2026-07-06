import requests
import json

from termucoder.config import load_config


class LLMClient:

    def __init__(self):

        config = load_config()

        host = config["server"]["host"]
        port = config["server"]["port"]

        self.url = f"http://{host}:{port}"

        self.temperature = (
            config["generation"]["temperature"]
        )

        self.max_tokens = (
            config["generation"]["max_tokens"]
        )


    def ask(self, prompt):

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты AI помощник программиста. "
                        "Отвечай точно на запрос. "
                        "Если пользователь просит код — "
                        "выводи только код."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }


        result = ""


        try:

            with requests.post(
                self.url + "/v1/chat/completions",
                json=payload,
                stream=True,
                timeout=300
            ) as r:


                r.encoding = "utf-8"


                for line in r.iter_lines(
                    decode_unicode=True
                ):


                    if not line:
                        continue


                    if line.startswith("data: "):

                        data = line[6:]


                        if data == "[DONE]":
                            break


                        try:

                            obj = json.loads(data)


                            text = (
                                obj["choices"][0]
                                ["delta"]
                                .get("content", "")
                            )


                            if text:

                                print(
                                    text,
                                    end="",
                                    flush=True
                                )

                                result += text


                        except json.JSONDecodeError:
                            pass


        except requests.exceptions.ConnectionError:

            print(
                "\n❌ AI сервер недоступен"
            )


        return result
