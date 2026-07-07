"""Общие вспомогательные функции TermuCoderAI.

Здесь собраны простые хелперы, используемые разными модулями проекта:
цветной вывод, парсинг .gitignore и проверка игнорирования путей.
"""

from __future__ import annotations

import os
import sys

# ANSI-коды цветов. Работают в большинстве терминалов, включая Termux.
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"


def supports_color() -> bool:
    """Возвращает True, если терминал поддерживает цвета."""
    return sys.stdout.isatty()


def _paint(code: str, text: str) -> str:
    if supports_color():
        return f"{code}{text}{RESET}"
    return text


def ok(text: str) -> str:
    return _paint(GREEN, "[OK] " + text)


def error(text: str) -> str:
    return _paint(RED, "[ERR] " + text)


def warning(text: str) -> str:
    return _paint(YELLOW, "[!] " + text)


def note(text: str) -> str:
    return _paint(BLUE, "[i] " + text)


def header(text: str) -> str:
    return _paint(BOLD + CYAN, text)


def muted(text: str) -> str:
    return _paint(DIM, text)


# ---------------------------------------------------------------------------
# Работа с .gitignore
# ---------------------------------------------------------------------------

def read_gitignore(root: str = ".") -> "set[str]":
    """Читает паттерны из .gitignore в указанной директории.

    Возвращает множество паттернов (без комментариев и пустых строк).
    Если файла нет — возвращает пустое множество.
    """
    patterns: "set[str]" = set()
    path = os.path.join(root, ".gitignore")

    if not os.path.isfile(path):
        return patterns

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            patterns.add(line.rstrip("/"))

    return patterns


def _norm(path: str) -> str:
    return path.replace(os.sep, "/").strip("/").lstrip("./").strip("/")


def is_ignored(rel_path: str, patterns: "set[str]") -> bool:
    """Проверяет, попадает ли относительный путь под паттерны .gitignore.

    Поддерживаются:
      - точное совпадение        ("foo.txt")
      - совпадение директории    ("build/" -> "build/...")
      - совпадение по имени файла ("foo.txt" в любой вложенности)
      - суффиксные маски         ("*.pyc", ".*")
    """
    rel = _norm(rel_path)

    if not rel:
        return False

    parts = rel.split("/")

    for pat in patterns:
        if not pat:
            continue

        if pat == rel:
            return True

        if rel.startswith(pat + "/"):
            return True

        if parts[-1] == pat:
            return True

        if pat.startswith("*"):
            suffix = pat[1:]

            if rel.endswith(suffix) or any(
                p.endswith(suffix) for p in parts
            ):
                return True

    return False
