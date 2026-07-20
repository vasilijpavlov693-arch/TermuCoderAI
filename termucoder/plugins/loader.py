"""Загрузчик плагинов TermuCoderAI (v0.7).

Сканирует директории плагинов и загружает их через importlib.
"""

import os
import sys
import importlib.util
import json


PLUGIN_DIRS = [
    os.path.expanduser("~/.termucoder/plugins"),
    os.path.join(".termucoder", "plugins"),
]


def _find_plugins(directory):
    """Находит плагины в указанной директории."""
    plugins = []

    if not os.path.isdir(directory):
        return plugins

    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        init_path = os.path.join(path, "__init__.py")

        if os.path.isdir(path) and os.path.isfile(init_path):
            meta = {}
            meta_path = os.path.join(path, "plugin.json")
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass

            plugins.append({
                "name": meta.get("name", name),
                "version": meta.get("version", "0.0.0"),
                "description": meta.get("description", ""),
                "path": path,
                "init": init_path,
            })

    return plugins


def load_plugins(registry):
    """Загружает все плагины из всех директорий."""
    loaded = []
    seen = set()

    for directory in PLUGIN_DIRS:
        for plugin in _find_plugins(directory):
            name = plugin["name"]
            if name in seen:
                continue
            seen.add(name)

            try:
                spec = importlib.util.spec_from_file_location(
                    f"termucoder_plugin_{name}",
                    plugin["init"]
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                if hasattr(module, "register"):
                    module.register(registry)
                    loaded.append(plugin)
            except Exception:
                continue

    return loaded
