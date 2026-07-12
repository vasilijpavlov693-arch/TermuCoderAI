"""Работа с изменениями кода TermuCoderAI.

Модуль v0.5:
- создание diff между версиями файла
- подготовка безопасного применения изменений
"""

import difflib
from pathlib import Path


def read_file(path):
    """Читает текстовый файл."""
    return Path(path).read_text(
        encoding="utf-8"
    )


def write_file(path, content):
    """Записывает текстовый файл."""
    Path(path).write_text(
        content,
        encoding="utf-8"
    )


def create_diff(
    old_text,
    new_text,
    filename="file"
):
    """Создаёт unified diff."""

    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile=filename,
        tofile=filename,
        lineterm=""
    )

    return "\n".join(diff)


def file_diff(
    path,
    new_content
):
    """Создаёт diff для существующего файла."""

    old_content = read_file(path)

    return create_diff(
        old_content,
        new_content,
        str(path)
    )


def apply_content(
    path,
    new_content
):
    """Применяет новое содержимое файла."""

    write_file(
        path,
        new_content
    )
