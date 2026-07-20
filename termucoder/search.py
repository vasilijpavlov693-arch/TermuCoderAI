"""Поиск и сканирование файлов проекта (v0.4).

Модуль обходит директорию проекта, учитывает .gitignore и стандартные
игнорируемые папки (например .git, __pycache__, node_modules).
"""

import functools
import os

from termucoder.utils import read_gitignore, is_ignored


# Директории, которые всегда пропускаем при сканировании.
DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    ".termucoder",
    ".mimocode",
    "cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
}


def scan_project(root: str = ".", extra_ignore=None) -> "list[str]":
    """Возвращает отсортированный список файлов проекта (относительные пути).

    Учитываются паттерны из .gitignore и DEFAULT_IGNORE_DIRS.
    """
    patterns = read_gitignore(root)

    if extra_ignore:
        patterns |= set(extra_ignore)

    results: "list[str]" = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Отсекаем игнорируемые директории на месте, чтобы не заходить внутрь.
        dirnames[:] = [
            d for d in dirnames
            if d not in DEFAULT_IGNORE_DIRS
            and not is_ignored(os.path.join(rel_dir, d), patterns)
        ]

        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), root)

            if is_ignored(rel, patterns):
                continue

            results.append(rel.replace(os.sep, "/"))

    return sorted(results)


def count_by_ext(files: "list[str]") -> "dict[str, int]":
    """Возвращает статистику количества файлов по расширениям."""
    stats: "dict[str, int]" = {}

    for f in files:
        ext = os.path.splitext(f)[1].lower() or "(без расширения)"
        stats[ext] = stats.get(ext, 0) + 1

    return stats
