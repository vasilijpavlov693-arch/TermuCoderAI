"""Инструмент: запись/создание файла."""
import os
from termucoder.tools import Tool


class WriteFileTool(Tool):
    name = "write_file"
    description = "Записывает содержимое в файл. Создаёт файл или перезаписывает."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Путь к файлу"},
            "content": {"type": "string", "description": "Содержимое файла"},
        },
        "required": ["path", "content"],
    }

    def execute(self, path: str = "", content: str = "", **kw) -> str:
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Файл записан: {path} ({len(content)} байт)"
        except Exception as e:
            return f"Ошибка записи {path}: {e}"
