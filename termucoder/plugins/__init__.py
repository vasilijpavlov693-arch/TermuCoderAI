"""Система плагинов TermuCoderAI (v0.7).

Плагины — Python-пакеты с функцией register(registry).
Хранятся в ~/.termucoder/plugins/ (глобальные) и .termucoder/plugins/ (проектные).
"""

import os
import importlib.util


class PluginRegistry:
    """Центральный реестр для регистрации плагинов."""

    def __init__(self):
        self.commands = {}
        self.prompts = {}
        self.hooks = {}
        self.config_defaults = {}

    def add_command(self, name, handler, help_text=""):
        """Регистрирует новую CLI-команду."""
        self.commands[name] = {"handler": handler, "help": help_text}

    def add_prompt(self, name, text):
        """Регистрирует именованный шаблон промпта."""
        self.prompts[name] = text

    def add_hook(self, event, callback):
        """Регистрирует callback для события (before_ask, after_ask, etc.)."""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)

    def add_config_defaults(self, section, defaults):
        """Регистрирует дефолты для секции конфигурации."""
        self.config_defaults[section] = defaults

    def get_prompt(self, name):
        """Возвращает шаблон промпта по имени или None."""
        return self.prompts.get(name)

    def run_hooks(self, event, *args, **kwargs):
        """Вызывает все callbacks для события."""
        for cb in self.hooks.get(event, []):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass
