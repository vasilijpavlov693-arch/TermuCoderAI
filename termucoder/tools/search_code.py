"""Инструмент: поиск по коду (grep)."""
import os
import re
from termucoder.tools import Tool


class SearchCodeTool(Tool):
    name = "search_code"
    description = "Ищет совпадения регулярного выражения в файлах проекта."
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Regex паттерн для поиска"},
            "path": {"type": "string", "description": "Директория для поиска (по умолчанию .)"},
            "include": {"type": "string", "description": "Фильтр по расширению (например *.py)"},
        },
        "required": ["pattern"],
    }

    def execute(self, pattern: str = "", path: str = ".", include: str = "", **kw) -> str:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"Ошибка regex: {e}"

        skip = {".git", "node_modules", "__pycache__", ".termucoder"}
        results = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in skip]
            for fn in files:
                if include and not fn.endswith(include.replace("*", "")):
                    continue
                filepath = os.path.join(root, fn)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append(f"{filepath}:{i}: {line.rstrip()}")
                except Exception:
                    continue

        if not results:
            return "Ничего не найдено"
        return chr(10).join(results[:50])
