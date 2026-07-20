"""Работа с номером версии TermuCoderAI."""

import os

from termucoder.utils import header, success, muted


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
    "analyze (анализ проектов)",
]


def show_version():
    print(header(f"TermuCoderAI {get_version()}"))
    print()

    for feature in FEATURES:
        print(f"  {success(feature)}")
