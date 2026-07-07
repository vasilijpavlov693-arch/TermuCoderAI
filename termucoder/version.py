"""Работа с номером версии TermuCoderAI."""

import os


VERSION_FILE = "VERSION"


def get_version() -> str:
    """Возвращает версию из файла VERSION или 'unknown'."""
    if not os.path.exists(VERSION_FILE):
        return "unknown"

    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


# Список реализованных возможностей (для вывода в --version и doctor).
FEATURES = [
    "llama-server manager",
    "model manager",
    "doctor (диагностика)",
    "setup (настройка)",
    "config (настройки)",
    "chat (интерактивный режим)",
]


def show_version():
    print(f"TermuCoderAI {get_version()}")
    print()

    for feature in FEATURES:
        print(f"  ✓ {feature}")
