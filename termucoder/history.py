"""Управление историей диалогов TermuCoderAI (v0.3).

Сессии хранятся в директории ``history/`` в виде JSON-файлов. Каждая сессия
содержит список сообщений в формате {"role": "user"/"assistant", "content": ...}.
"""

import json
import os
import time


HISTORY_DIR = "history"
SESSION_EXT = ".json"

# Допустимые символы в id сессии (исключаем "/", "\\", ".." и пр.).
_ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")


def _validate(session_id: str) -> None:
    if not session_id or not all(c in _ALLOWED for c in session_id):
        raise ValueError(f"Недопустимый id сессии: {session_id!r}")


def session_path(session_id: str) -> str:
    """Возвращает путь к файлу сессии. Выбрасывает ValueError при невалидном id."""
    _validate(session_id)
    return os.path.join(HISTORY_DIR, session_id + SESSION_EXT)


def new_session_id() -> str:
    """Генерирует идентификатор сессии на основе текущего времени."""
    return time.strftime("%Y%m%d-%H%M%S")


def save_session(session_id: str, messages: list) -> None:
    """Сохраняет список сообщений сессии в файл."""
    try:
        path = session_path(session_id)
    except ValueError:
        return

    _ensure_dir()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"id": session_id, "messages": messages},
            f,
            ensure_ascii=False,
            indent=2
        )


def load_session(session_id: str) -> list:
    """Загружает сообщения сессии. Возвращает [] при ошибках/отсутствии файла."""
    try:
        path = session_path(session_id)
    except ValueError:
        return []

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("messages", [])
    except (json.JSONDecodeError, OSError):
        return []


def list_sessions() -> "list[str]":
    """Возвращает список идентификаторов сессий (отсортированных)."""
    if not os.path.isdir(HISTORY_DIR):
        return []

    sessions = [
        fn[: -len(SESSION_EXT)]
        for fn in os.listdir(HISTORY_DIR)
        if fn.endswith(SESSION_EXT)
    ]

    return sorted(sessions)


def latest_session():
    """Возвращает id последней сессии или None."""
    sessions = list_sessions()
    return sessions[-1] if sessions else None


def delete_session(session_id: str) -> bool:
    """Удаляет сессию. Возвращает True, если файл был удалён."""
    try:
        path = session_path(session_id)
    except ValueError:
        return False

    if os.path.exists(path):
        os.remove(path)
        return True

    return False


def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)
