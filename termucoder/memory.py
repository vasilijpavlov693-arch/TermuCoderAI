"""Память проектов TermuCoderAI (v1.3).

Локальное хранилище знаний о проекте. Записи хранятся в
.termucoder/memory/ в виде JSON-файлов.

Типы записей:
  - manual   — пользователь добавил вручную
  - chat     — извлечено из диалога с моделью
  - analyze  — вывод из анализа проекта
"""

import json
import math
import os
import re
import time


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


def _tokenize(text: str) -> list:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_]+", text.lower())


def _compute_idf(documents: list) -> dict:
    n_docs = len(documents)
    if n_docs == 0:
        return {}
    df = {}
    for doc in documents:
        tokens = set(_tokenize(doc))
        for token in tokens:
            df[token] = df.get(token, 0) + 1
    idf = {}
    for token, freq in df.items():
        idf[token] = math.log((n_docs + 1) / (freq + 1)) + 1
    return idf


def _tfidf_score(query_tokens: list, doc_tokens: list, idf: dict) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    doc_token_counts = {}
    for t in doc_tokens:
        doc_token_counts[t] = doc_token_counts.get(t, 0) + 1
    score = 0.0
    for qt in query_tokens:
        if qt in idf:
            tf = doc_token_counts.get(qt, 0) / len(doc_tokens)
            score += tf * idf[qt]
    return score


def add(content: str, tags: list = None, source: str = "manual") -> dict:
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


def find_similar(content: str, threshold: float = 0.7) -> dict:
    entries = list_all()
    if not entries:
        return None
    query_tokens = set(_tokenize(content))
    if not query_tokens:
        return None
    best_entry = None
    best_ratio = 0.0
    for entry in entries:
        entry_tokens = set(_tokenize(entry.get("content", "")))
        if not entry_tokens:
            continue
        intersection = query_tokens & entry_tokens
        union = query_tokens | entry_tokens
        ratio = len(intersection) / len(union) if union else 0
        if ratio > best_ratio:
            best_ratio = ratio
            best_entry = entry
    if best_ratio >= threshold:
        return best_entry
    return None


def get(entry_id: str) -> dict:
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
    try:
        _validate_id(entry_id)
    except ValueError:
        return False
    path = _entry_path(entry_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def list_all() -> list:
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


def search(query: str, max_results: int = 20) -> list:
    entries = list_all()
    if not entries:
        return []
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    all_docs = [e.get("content", "") for e in entries]
    idf = _compute_idf(all_docs)
    scored = []
    for entry, doc in zip(entries, all_docs):
        doc_tokens = _tokenize(doc)
        score = _tfidf_score(query_tokens, doc_tokens, idf)
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda x: -x[0])
    if scored:
        return [e for _, e in scored[:max_results]]
    query_lower = query.lower()
    return [e for e in entries if query_lower in e.get("content", "").lower()][:max_results]


def list_by_tag(tag: str) -> list:
    tag_lower = tag.lower()
    return [e for e in list_all() if tag_lower in [t.lower() for t in e.get("tags", [])]]


def get_all_tags() -> dict:
    tags = {}
    for entry in list_all():
        for tag in entry.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    return dict(sorted(tags.items(), key=lambda x: -x[1]))


def get_context(max_entries: int = 10, query: str = None) -> str:
    entries = list_all()
    if not entries:
        return ""
    if query:
        relevant = search(query, max_results=max_entries)
    else:
        relevant = entries[-max_entries:]
    lines = []
    for entry in relevant:
        tags = ", ".join(entry.get("tags", []))
        source = entry.get("source", "manual")
        content = entry.get("content", "")
        lines.append(f"- [{source}] {content}" + (f" (теги: {tags})" if tags else ""))
    return "\n".join(lines)


def export_all(filepath: str) -> int:
    entries = list_all()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    return len(entries)


def import_all(filepath: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        entries = json.load(f)
    _ensure_dir()
    imported = 0
    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry:
            continue
        entry_id = entry["id"]
        path = _entry_path(entry_id)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
            imported += 1
    return imported


def count() -> int:
    if not os.path.isdir(MEMORY_DIR):
        return 0
    return len([f for f in os.listdir(MEMORY_DIR) if f.endswith(EXTENSION)])
