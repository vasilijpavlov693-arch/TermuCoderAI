"""Инструмент: список файлов."""
import os
from termucoder.tools import Tool


class ListFilesTool(Tool):
    name = "list_files"
    description = "Показывает список файлов в директории."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Путь к директории (по умолчанию .)"},
            "pattern": {"type": "string", "description": "Фильтр по расширению (например *.py)"},
        },
        "required": [],
    }

    def execute(self, path: str = ".", pattern: str = "", **kw) -> str:
        try:
            entries = []
            for fn in sorted(os.listdir(path)):
                full = os.path.join(path, fn)
                if os.path.isdir(full):
                    entries.append(f"  {fn}/")
                elif not pattern or fn.endswith(pattern.replace("*", "")):
                    entries.append(f"  {fn}")
            if not entries:
                return "Директория пуста"
            return chr(10).join(entries[:100])
        except Exception as e:
            return f"Ошибка: {e}"
