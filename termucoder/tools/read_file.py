"""Инструмент: чтение файла."""
from termucoder.tools import Tool


class ReadFileTool(Tool):
    name = "read_file"
    description = "Читает содержимое файла. Можно указать диапазон строк."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Путь к файлу"},
            "start_line": {"type": "integer", "description": "Начальная строка (с 1)"},
            "end_line": {"type": "integer", "description": "Конечная строка"},
        },
        "required": ["path"],
    }

    def execute(self, path: str = "", start_line: int = 1, end_line: int = 0, **kw) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            if end_line <= 0:
                end_line = len(lines)
            selected = lines[start_line - 1 : end_line]
            result = []
            for i, line in enumerate(selected, start=start_line):
                result.append(f"{i}: {line.rstrip()}")
            return chr(10).join(result)
        except FileNotFoundError:
            return f"Ошибка: файл не найден: {path}"
        except Exception as e:
            return f"Ошибка чтения {path}: {e}"
