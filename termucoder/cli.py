"""CLI интерфейс TermuCoderAI (v0.2 — Стабильное ядро).

Единая точка входа. Поддерживает команды: ask, config, server, model, setup,
doctor, а также флаги --version / --help.

Примеры:
    termucoder --version
    termucoder --help
    termucoder ask "объясни этот код"
    termucoder config show
    termucoder config set generation.temperature 0.4
    termucoder doctor
"""

import sys

from termucoder.api import LLMClient
from termucoder.config import (
    load_config,
    save_config,
    init_config,
    set_value,
    get_value
)
from termucoder.server import (
    start_server,
    stop_server,
    status_server,
    restart_server
)
from termucoder.doctor import doctor
from termucoder.setup import setup
from termucoder.version import show_version, get_version
from termucoder.model import (
    list_models,
    info_model,
    use_model
)
from termucoder.utils import ok, error, warning, note, header, muted


# ---------------------------------------------------------------------------
# Команды
# ---------------------------------------------------------------------------

def config_command(args):
    """Управление настройками: show / set / init."""
    if len(args) == 0:
        cfg = load_config()
        print()
        print(header("⚙ TermuCoderAI config:"))
        print()

        for section, values in cfg.items():
            print(f"[{section}]")

            if isinstance(values, dict):
                for k, v in values.items():
                    print(f"  {k} = {v}")
            else:
                print(f"  {values}")

            print()
        return

    action = args[0]

    if action == "init":
        init_config()
        return

    if action == "show":
        if len(args) < 2:
            config_command([])
            return

        key = args[1]
        cfg = load_config()

        try:
            value = get_value(cfg, key)
        except ValueError:
            print(error("Формат: termucoder config show section.key"))
            return

        print(f"{key} = {value}")
        return

    if action == "set":
        if len(args) < 3:
            print(error("Использование: termucoder config set section.key value"))
            return

        key = args[1]
        value = " ".join(args[2:])

        cfg = load_config()

        try:
            set_value(cfg, key, value)
        except ValueError:
            print(error("Формат ключа: section.key (например model.name)"))
            return

        save_config(cfg)
        print(ok(f"Настройка изменена: {key}"))
        return

    print(error(f"Неизвестная подкоманда config: {action}"))


def server_command(args):
    """Управление llama-server: start / stop / restart / status."""
    if len(args) == 0:
        print("Использование:\n"
              "  termucoder server start\n"
              "  termucoder server stop\n"
              "  termucoder server restart\n"
              "  termucoder server status")
        return

    action = args[0]

    if action == "start":
        start_server()
    elif action == "stop":
        stop_server()
    elif action == "restart":
        restart_server()
    elif action == "status":
        status_server()
    else:
        print(error(f"Неизвестная команда сервера: {action}"))


def model_command(args):
    """Управление моделями: list / info / use."""
    if len(args) == 0:
        print("Использование:\n"
              "  termucoder model list\n"
              "  termucoder model info\n"
              "  termucoder model use <name>")
        return

    action = args[0]

    if action == "list":
        list_models()
    elif action == "info":
        info_model()
    elif action == "use":
        if len(args) < 2:
            print(error("Укажи имя модели"))
            return
        use_model(args[1])
    else:
        print(error(f"Неизвестная команда модели: {action}"))


def ask_command(args):
    """Одиночный вопрос модели."""
    prompt = " ".join(args)

    if not prompt:
        print(error("Укажи текст запроса: termucoder ask \"... \""))
        return

    client = LLMClient()
    print()
    client.ask(prompt)
    print()


# ---------------------------------------------------------------------------
# Справка
# ---------------------------------------------------------------------------

COMMANDS_HELP = [
    ("ask <текст>",            "Задать модели одиночный вопрос"),
    ("config",                 "Показать настройки (show/set/init)"),
    ("server <команда>",      "Управление llama-server (start/stop/restart/status)"),
    ("model <команда>",       "Управление моделями (list/info/use)"),
    ("setup [--full]",         "Настройка окружения"),
    ("doctor",                 "Диагностика системы"),
    ("--version, -v",          "Показать версию"),
    ("--help, -h",             "Показать эту справку"),
]


def print_help():
    print(header(f"TermuCoderAI {get_version()}"))
    print()
    print("Использование: termucoder <команда> [аргументы]")
    print()
    print("Команды:")
    for name, desc in COMMANDS_HELP:
        print(f"  {name:<22} {desc}")
    print()
    print("Примеры:")
    print("  termucoder ask \"объясни этот код\"")
    print("  termucoder config set generation.temperature 0.4")
    print("  termucoder doctor")


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

def main():
    argv = sys.argv[1:]

    # Глобальные флаги.
    if not argv or argv[0] in ("--help", "-h", "help"):
        print_help()
        return

    if argv[0] in ("--version", "-v", "version"):
        show_version()
        return

    command = argv[0]
    rest = argv[1:]

    handlers = {
        "ask": ask_command,
        "config": config_command,
        "server": server_command,
        "model": model_command,
        "setup": lambda a: setup("--full" in a, "--start" in a),
        "doctor": lambda a: doctor(),
    }

    handler = handlers.get(command)

    if handler is None:
        # Обратная совместимость: любой неизвестный первый аргумент
        # считаем текстом запроса.
        ask_command(argv)
        return

    try:
        handler(rest)
    except KeyboardInterrupt:
        print(warning("\nПрервано пользователем"))
        sys.exit(130)
    except FileNotFoundError as exc:
        print(error(f"Файл не найден: {exc}"))
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(error(f"Ошибка: {exc}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
