import os
import json
import subprocess
import importlib.util

from termucoder.server import start_server, status_server
from termucoder.config import (
    load_config,
    save_config,
    init_config,
    DEFAULT_CONFIG,
    CONFIG_FILE,
)


MODELS_DIR = os.path.expanduser(
    "~/AI/models"
)

LLAMA_DIR = os.path.expanduser(
    "~/AI/llama.cpp"
)

LLAMA_SERVER = os.path.join(
    LLAMA_DIR,
    "build/bin/llama-server"
)


def create_dirs():

    os.makedirs(
        MODELS_DIR,
        exist_ok=True
    )

    print(
        "✓ Папка моделей:",
        MODELS_DIR
    )



def create_config():

    if os.path.exists(CONFIG_FILE):

        print(
            "✓ settings.json уже существует"
        )

        return


    save_config(
        DEFAULT_CONFIG
    )

    print(
        "✓ settings.json создан"
    )



def check_python():

    try:

        version = subprocess.check_output(
            [
                "python",
                "--version"
            ],
            text=True
        )

        print(
            "✓",
            version.strip()
        )

    except:

        print(
            "✗ Python не найден"
        )



def check_package(name):

    if importlib.util.find_spec(name):

        print(
            "✓ Python пакет:",
            name
        )

    else:

        print(
            "⚠ Нет Python пакета:",
            name
        )



def check_llama():

    if os.path.exists(LLAMA_SERVER):

        print(
            "✓ llama-server"
        )

    else:

        print(
            "⚠ llama-server не найден"
        )



def find_models():

    if not os.path.exists(MODELS_DIR):

        return []


    return [

        x for x in os.listdir(MODELS_DIR)

        if x.endswith(".gguf")

    ]



def setup_model():

    models = find_models()


    if not models:

        print(
            "⚠ GGUF модели не найдены"
        )

        return


    cfg = load_config()


    current = cfg.get(
        "model",
        {}
    ).get(
        "path",
        ""
    )


    if current:

        print(
            "✓ Модель уже выбрана"
        )

        return


    name = models[0]


    cfg["model"]["name"] = name

    cfg["model"]["path"] = (
        "~/AI/models/" + name
    )


    save_config(
        cfg
    )


    print(
        "✓ Выбрана модель:",
        name
    )



def basic_setup():

    print()
    print(
        "🛠 TermuCoderAI setup"
    )
    print()


    create_dirs()

    create_config()

    check_llama()

    models = find_models()


    if models:

        print(
            "✓ Найдены модели:"
        )

        for m in models:

            print(
                "  -",
                m
            )

    else:

        print(
            "⚠ GGUF модели не найдены"
        )


    print()

    print(
        "✅ Настройка завершена"
    )



def full_setup():

    print()
    print(
        "🚀 TermuCoderAI full setup"
    )
    print()


    create_dirs()

    create_config()

    check_python()

    check_package(
        "requests"
    )

    check_llama()

    setup_model()


    print()

    print(
        "✅ Полная настройка завершена"
    )



def setup(full=False, start=False):

    if full:

        full_setup()

    else:

        basic_setup()


    if start:

        print()

        print(
            "🚀 Запуск llama-server..."
        )

        start_server()

        print()

        status_server()
