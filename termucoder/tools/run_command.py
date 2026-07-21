"""Инструмент: запуск shell-команды."""
import subprocess
import sys
from termucoder.tools import Tool


class RunCommandTool(Tool):
    name = "run_command"
    description = "Запускает shell-команду и возвращает вывод."
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Команда для выполнения"},
            "timeout": {"type": "integer", "description": "Таймаут в секундах (по умолчанию 30)"},
        },
        "required": ["command"],
    }

    def execute(self, command: str = "", timeout: int = 30, **kw) -> str:
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, creationflags=flags,
            )
            output = result.stdout
            if result.stderr:
                output += chr(10) + "STDERR: " + result.stderr
            if not output.strip():
                output = "(пустой вывод)"
            return output[:5000]
        except subprocess.TimeoutExpired:
            return f"Таймаут ({timeout}с)"
        except Exception as e:
            return f"Ошибка: {e}"
