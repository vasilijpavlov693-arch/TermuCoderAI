"""Управление историей диалогов TermuCoderAI (v0.3).

Сессии хранятся в директории ``history/`` в виде JSON-файлов. Каждая сессия
содержит список сообщений в формате {"role": "user"/"assistant", "content": ...}.
"""

import json
import os
import time


HISTORY_DIR = "history"
SESSION_EXT = ".json"


def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def session_path(session_id: str) -> str:
    return os.path.join(HISTORY_DIR, session_id + SESSION_EXT)


def new_session_id() -> str:
    """Генерирует идентификатор сессии на основе текущего времени."""
    return time.strftime("%Y%m%d-%H%M%S")


def save_session(session_id: str, messages: list) -> None:
    """Сохраняет список сообщений сессии в файл."""
    _ensure_dir()

    with open(session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(
            {"id": session_id, "messages": messages},
            f,
            ensure_ascii=False,
            indent=2
        )


def load_session(session_id: str) -> list:
    """Загружает сообщения сессии. Если сессии нет — возвращает []."""
    path = session_path(session_id)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("messages", [])


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
    path = session_path(session_id)

    if os.path.exists(path):
        os.remove(path)
        return True

    return False
