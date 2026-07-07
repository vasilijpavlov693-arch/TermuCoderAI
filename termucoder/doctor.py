import os
import json
import subprocess
import urllib.request

from termucoder.config import load_config, CONFIG_FILE

def check_settings():

    if os.path.exists(CONFIG_FILE):

        print("✓ settings.json")

        return True

    print("✗ settings.json отсутствует")

    return False



def check_model():

    cfg = load_config()

    path = cfg.get(
        "model",
        {}
    ).get(
        "path",
        ""
    )


    path = os.path.expanduser(
        path
    )


    if os.path.exists(path):

        print(
            "✓ Модель:",
            os.path.basename(path)
        )

        return True


    print(
        "✗ Модель не найдена:",
        path
    )

    return False



def check_llama():

    cfg = load_config()

    path = os.path.expanduser(
        "~/AI/llama.cpp/build/bin/llama-server"
    )


    if os.path.exists(path):

        print(
            "✓ llama-server"
        )

        return True


    print(
        "✗ llama-server не найден"
    )

    return False



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

        return True


    except:

        print(
            "✗ Python"
        )

        return False



def check_api():

    cfg = load_config()

    host = cfg.get(
        "server",
        {}
    ).get(
        "host",
        "127.0.0.1"
    )

    port = cfg.get(
        "server",
        {}
    ).get(
        "port",
        8080
    )


    url = (
        f"http://{host}:{port}/health"
    )


    try:

        urllib.request.urlopen(
            url,
            timeout=3
        )

        print(
            "✓ llama-server API"
        )

        return True


    except:

        print(
            "✗ llama-server API недоступен"
        )

        return False



def doctor():

    print()
    print(
        "🩺 TermuCoderAI doctor"
    )
    print()


    checks = [

        check_settings(),

        check_python(),

        check_llama(),

        check_model(),

        check_api()

    ]


    print()

    if all(checks):

        print(
            "✅ Система готова"
        )

    else:

        print(
            "⚠ Найдены проблемы"
        )
