"""Работа с настройками TermuCoderAI.

Настройки хранятся в settings.json в текущей директории. Модуль предоставляет
загрузку/сохранение конфигурации, а также удобные хелперы для чтения и записи
вложенных значений в формате ``section.key``.
"""

import copy
import json
import os


CONFIG_FILE = "settings.json"


DEFAULT_CONFIG = {
    "server": {
        "host": "127.0.0.1",
        "port": 8080,
        "context": 4096,
        "threads": 4,
        "gpu_layers": 0,
        "parallel": 1
    },

    "model": {
        "name": "",
        "path": ""
    },

    "generation": {
        "temperature": 0.2,
        "max_tokens": 512,
        "top_p": 0.9,
        "top_k": 40
    },

    "prompts": {
        "system": "Ты AI помощник программиста."
    },

    "user": {
        "language": "ru",
        "editor": "",
        "auto_save_history": True
    }
}


def load_config():
    """Загружает конфигурацию. Если файла нет — возвращает значения по умолчанию."""
    if not os.path.exists(CONFIG_FILE):
        # Возвращаем копию, чтобы мутации не портили глобальные умолчания.
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG

    # Дополняем отсутствующие секции значениями по умолчанию.
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def save_config(config):
    """Сохраняет конфигурацию в settings.json с отступами."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def init_config():
    """Создаёт settings.json, если он ещё не существует."""
    if os.path.exists(CONFIG_FILE):
        print("[!] settings.json уже существует")
        return

    save_config(DEFAULT_CONFIG)
    print("[OK] settings.json создан")


def _coerce(value: str):
    """Преобразует строковое значение в подходящий Python-тип."""
    low = value.lower()

    if low in ("true", "false"):
        return low == "true"

    if low in ("none", "null", ""):
        return None

    try:
        if "." in value or "e" in value.lower():
            return float(value)

        return int(value)
    except ValueError:
        return value


def set_value(config, key: str, value):
    """Устанавливает вложенное значение вида ``section.key``.

    Возвращает изменённый config. Тип значения определяется автоматически.
    """
    parts = key.split(".")

    if len(parts) != 2:
        raise ValueError("Формат ключа: section.key")

    section, name = parts

    if section not in config or not isinstance(config[section], dict):
        config[section] = {}

    config[section][name] = _coerce(value)

    return config


def get_value(config, key: str, default=None):
    """Возвращает вложенное значение вида ``section.key`` или default."""
    parts = key.split(".")

    if len(parts) != 2:
        raise ValueError("Формат ключа: section.key")

    section, name = parts

    return config.get(section, {}).get(name, default)
