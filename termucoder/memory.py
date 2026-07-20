"""Память проектов TermuCoderAI (v0.6).

Локальное хранилище знаний о проекте. Записи хранятся в
``.termucoder/memory/`` в виде JSON-файлов.

Типы записей:
  - manual   — пользователь добавил вручную
  - chat     — извлечено из диалога с моделью
  - analyze  — вывод из анализа проекта
"""

import json
import os
import time
import random


MEMORY_DIR = os.path.join(".termucoder", "memory")
EXTENSION = ".json"


def _ensure_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def _entry_path(entry_id: str) -> str:
    return os.path.join(MEMORY_DIR, entry_id + EXTENSION)


def _validate_id(entry_id: str) -> None:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")
    if not entry_id or not all(c in allowed for c in entry_id):
        raise ValueError(f"Недопустимый id: {entry_id!r}")


def add(content: str, tags: "list[str]" = None, source: str = "manual") -> dict:
    """Добавляет запись в память проекта."""
    _ensure_dir()

    ts = time.strftime("%Y%m%d-%H%M%S")
    seq = f"{count():04d}"
    entry_id = f"{ts}-{seq}"

    entry = {
        "id": entry_id,
        "content": content.strip(),
        "tags": tags or [],
        "source": source,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    path = _entry_path(entry_id)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    return entry


def get(entry_id: str) -> "dict | None":
    """Возвращает запись по ID или None."""
    try:
        _validate_id(entry_id)
    except ValueError:
        return None

    path = _entry_path(entry_id)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def delete(entry_id: str) -> bool:
    """Удаляет запись. Возвращает True если удалена."""
    try:
        _validate_id(entry_id)
    except ValueError:
        return False

    path = _entry_path(entry_id)

    if os.path.exists(path):
        os.remove(path)
        return True

    return False


def list_all() -> "list[dict]":
    """Возвращает все записи, отсортированные по ID (хронологически)."""
    if not os.path.isdir(MEMORY_DIR):
        return []

    entries = []
    for fn in os.listdir(MEMORY_DIR):
        if not fn.endswith(EXTENSION):
            continue
        path = os.path.join(MEMORY_DIR, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue

    return sorted(entries, key=lambda e: e.get("id", ""))


def search(query: str) -> "list[dict]":
    """Ищет записи по содержимому (substring match, без учёта регистра)."""
    query_lower = query.lower()
    results = []
    for entry in list_all():
        if query_lower in entry.get("content", "").lower():
            results.append(entry)
    return results


def list_by_tag(tag: str) -> "list[dict]":
    """Возвращает записи с указанным тегом."""
    tag_lower = tag.lower()
    return [
        e for e in list_all()
        if tag_lower in [t.lower() for t in e.get("tags", [])]
    ]


def get_context(max_entries: int = 10) -> str:
    """Формирует текстовый контекст из последних знаний для подстановки в промпт."""
    entries = list_all()

    if not entries:
        return ""

    recent = entries[-max_entries:]

    lines = []
    for entry in recent:
        tags = ", ".join(entry.get("tags", []))
        source = entry.get("source", "manual")
        content = entry.get("content", "")
        lines.append(f"- [{source}] {content}" + (f" (теги: {tags})" if tags else ""))

    return "\n".join(lines)


def count() -> int:
    """Возвращает количество записей."""
    if not os.path.isdir(MEMORY_DIR):
        return 0
    return len([f for f in os.listdir(MEMORY_DIR) if f.endswith(EXTENSION)])
