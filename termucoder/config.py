import json
import os


CONFIG_FILE = "settings.json"


DEFAULT_CONFIG = {
    "server": {
        "host": "127.0.0.1",
        "port": 8080
    },

    "model": {
        "name": ""
    },

    "generation": {
        "temperature": 0.2,
        "max_tokens": 192
    },

    "prompts": {
        "system": "Ты AI помощник программиста."
    }
}


def load_config():

    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG


    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def save_config(config):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )



def init_config():

    if os.path.exists(CONFIG_FILE):

        print(
            "⚠ settings.json уже существует"
        )

        return


    save_config(DEFAULT_CONFIG)

    print(
        "✅ settings.json создан"
    )
