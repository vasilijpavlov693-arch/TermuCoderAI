import requests
import json


class LLMClient:

    def __init__(self, url="http://127.0.0.1:8080"):
        self.url = url


    def ask(self, prompt):

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Ты кодовый помощник. Выполняй запрос буквально. Если пользователь просит написать код — выводи только код без объяснений, комментариев и текста вокруг."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 192,
            "stream": True
        }


        with requests.post(
            self.url + "/v1/chat/completions",
            json=payload,
            stream=True
        ) as r:

            r.encoding = "utf-8"

            for line in r.iter_lines(decode_unicode=True):

                if not line:
                    continue

                if line.startswith("data: "):

                    data=line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        obj=json.loads(data)

                        text=obj["choices"][0]["delta"].get("content","")

                        if text:
                            print(text, end="", flush=True)

                    except:
                        pass
