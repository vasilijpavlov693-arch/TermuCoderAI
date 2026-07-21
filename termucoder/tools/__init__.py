"""Система инструментов для Agent Mode (v1.4).

Базовый класс Tool и реестр инструментов, которые LLM может
вызывать при выполнении многошаговых задач.
"""

import json


class Tool:
    """Базовый класс инструмента."""

    name: str = ""
    description: str = ""
    parameters: dict = {}

    def execute(self, **kwargs) -> str:
        raise NotImplementedError

    def to_schema(self) -> dict:
        """Возвращает JSON Schema для LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


class ToolRegistry:
    """Реестр доступных инструментов."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools.get(name)

    def list_tools(self) -> list:
        return list(self._tools.values())

    def list_schemas(self) -> list:
        return [t.to_schema() for t in self._tools.values()]

    def execute(self, name: str, **kwargs) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Ошибка: инструмент '{name}' не найден"
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return f"Ошибка выполнения {name}: {e}"

    def summary(self) -> str:
        """Краткое описание всех инструментов для промпта."""
        lines = []
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        return chr(10).join(lines)


def create_default_registry() -> ToolRegistry:
    """Создаёт реестр со всеми встроенными инструментами."""
    from termucoder.tools.read_file import ReadFileTool
    from termucoder.tools.write_file import WriteFileTool
    from termucoder.tools.search_code import SearchCodeTool
    from termucoder.tools.run_command import RunCommandTool
    from termucoder.tools.list_files import ListFilesTool

    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(SearchCodeTool())
    registry.register(RunCommandTool())
    registry.register(ListFilesTool())
    return registry
