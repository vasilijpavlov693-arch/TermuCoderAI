"""Автодополнение команд TermuCoderAI (v0.8).

Использует readline для tab-completion команд и аргументов.
"""

import os
try:
    import readline
except ImportError:
    readline = None

COMMANDS = [
    "ask", "edit", "chat", "memory", "plugin",
    "config", "server", "model", "setup", "doctor", "analyze",
]

SUBCOMMANDS = {
    "config": ["show", "set", "init"],
    "server": ["start", "stop", "restart", "status"],
    "model": ["list", "info", "use"],
    "memory": ["add", "list", "search", "delete", "context"],
    "plugin": ["list", "info"],
}

FLAGS = {
    "ask": [],
    "edit": ["--preview", "--undo"],
    "chat": ["--new", "--list", "--session", "--delete", "--no-memory"],
    "memory": ["--tags"],
    "config": [],
    "server": [],
    "model": [],
    "setup": ["--full", "--start"],
    "doctor": [],
    "analyze": ["--ask", "--json"],
}

GLOBAL_FLAGS = ["--help", "--version", "-h", "-v"]


def _get_command(args):
    """Возвращает текущую команду из аргументов."""
    for arg in args:
        if arg in COMMANDS:
            return arg
    return None


def _complete_path(text):
    """Автодополнение путей к файлам."""
    if not text:
        text = "./"

    matches = []
    dir_part = os.path.dirname(text) or "."
    file_part = os.path.basename(text)

    try:
        for name in os.listdir(dir_part):
            if name.startswith(file_part):
                full = os.path.join(dir_part, name)
                if os.path.isdir(full):
                    matches.append(name + "/")
                else:
                    matches.append(name)
    except OSError:
        pass

    return matches


class TermuCompleter:
    """Completer для readline."""

    def __init__(self):
        self.matches = []

    def complete(self, text, state):
        if state == 0:
            self.matches = self._get_matches(text)
        return self.matches[state] if state < len(self.matches) else None

    def _get_matches(self, text):
        line = readline.get_begidx()
        full_line = readline.get_line_buffer()
        args = full_line.split()

        if not args or (len(args) == 1 and not full_line.endswith(" ")):
            return [c for c in COMMANDS if c.startswith(text)]

        cmd = _get_command(args)

        if cmd == "edit" and len(args) >= 2:
            return _complete_path(text)

        if cmd == "analyze" and len(args) >= 2:
            return _complete_path(text)

        if cmd in SUBCOMMANDS:
            subs = SUBCOMMANDS[cmd]
            return [s for s in subs if s.startswith(text)]

        if cmd in FLAGS:
            flags = FLAGS[cmd] + GLOBAL_FLAGS
            return [f for f in flags if f.startswith(text)]

        return GLOBAL_FLAGS


def setup_completion():
    """Настраивает readline для автодополнения."""
    completer = TermuCompleter()

    readline.set_completer(completer.complete)
    readline.set_completer_delims(" \t\n")
    readline.parse_and_bind("tab: complete")

    readline.parse_and_bind("set editing-mode emacs")
