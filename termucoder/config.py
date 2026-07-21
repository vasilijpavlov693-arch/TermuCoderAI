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
        "top_k": 40,
        "stop": [
            "###",
            "User:",
            "Пользователь:"
        ]
    },

    "prompts": {
        "system": "Ты AI помощник программиста."
    },

    "user": {
        "language": "ru",
        "editor": "",
        "auto_save_history": True
    },

    "memory": {
        "enabled": True,
        "max_entries": 100,
        "auto_learn": True,
        "context_limit": 10
    },

    "agent": {
        "max_iterations": 10,
        "auto_approve": False
    }
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Рекурсивно сливает override в копию base (сохраняя вложенные дефолты)."""
    result = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_config():
    """Загружает конфигурацию. Если файла нет — возвращает значения по умолчанию."""
    if not os.path.exists(CONFIG_FILE):
        # Возвращаем копию, чтобы мутации не портили глобальные умолчания.
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Копия, а не глобальный объект, чтобы мутации не портили умолчания.
        return copy.deepcopy(DEFAULT_CONFIG)

    # Глубокое слияние: сохраняем вложенные дефолты для частичных settings.json.
    return _deep_merge(DEFAULT_CONFIG, data)


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

    if low in ("none", "null"):
        return None

    try:
        if "." in value or "e" in value.lower():
            return float(value)

        return int(value)
    except ValueError:
        return value


def set_value(config, key: str, value):
    """Устанавливает вложенное значение (произвольная глубина, например a.b.c).

    Возвращает изменённый config. Тип значения определяется автоматически.
    """
    parts = key.split(".")

    if len(parts) < 2:
        raise ValueError("Формат ключа: section.key[.subkey...]")

    node = config
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            node[part] = {}
        node = node[part]

    node[parts[-1]] = _coerce(value)

    return config


def get_value(config, key: str, default=None):
    """Возвращает вложенное значение (произвольная глубина) или default."""
    parts = key.split(".")

    if len(parts) < 2:
        raise ValueError("Формат ключа: section.key[.subkey...]")

    node = config
    for part in parts:
        if not isinstance(node, dict):
            return default
        node = node.get(part)
        if node is None:
            return default

    return node
