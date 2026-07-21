"""CLI интерфейс TermuCoderAI.

Единая точка входа. Поддерживает команды: ask, config, server, model, setup,
doctor, version, chat, analyze, а также флаги --version / --help.

Примеры:
    termucoder --version
    termucoder --help
    termucoder ask "объясни этот код"
    termucoder config show
    termucoder config set generation.temperature 0.4
    termucoder doctor
    termucoder chat
    termucoder analyze .
"""

import sys

from termucoder import history as history_mod
from termucoder import context as context_mod
from termucoder import memory as memory_mod
from termucoder.plugins import PluginRegistry
from termucoder.plugins.loader import load_plugins
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
from termucoder.editor import edit_file
from termucoder.completer import setup_completion


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


def _try_extract_memory(client, user_msg, assistant_reply):
    """Пытается извлечь важную информацию из диалога для памяти проекта."""
    from termucoder.config import load_config

    cfg = load_config()
    mem_cfg = cfg.get("memory", {})
    if not mem_cfg.get("enabled", True) or not mem_cfg.get("auto_learn", True):
        return

    try:
        extract_prompt = (
            "Проанализируй этот диалог. Если есть факт, который стоит "
            "запомнить о проекте (архитектура, зависимости, решения, "
            "конвенции) — верни ТОЛЬКО этот факт одним предложением. "
            "Если ничего важного нет — верни пустую строку.\n\n"
            f"Пользователь: {user_msg}\n"
            f"Ассистент: {assistant_reply[:500]}"
        )

        result = client.ask(extract_prompt)
        result = result.strip()

        if result and len(result) > 10 and result != "Пустая строка":
            from termucoder import memory as memory_mod
            memory_mod.add(result, source="chat")
    except Exception:
        pass


def chat_command(args):
    """Интерактивный чат с моделью (v0.6)."""
    flags = set(args)
    auto_memory = "--no-memory" not in flags

    if "--new" in flags:
        session_id = history_mod.new_session_id()
        messages = []
        print(ok(f"Новая сессия: {session_id}"))
    elif "--session" in flags:
        idx = args.index("--session")
        if idx + 1 >= len(args):
            print(error("Укажи id сессии: termucoder chat --session <id>"))
            return
        session_id = args[idx + 1]
        messages = history_mod.load_session(session_id)
        print(ok(f"Продолжаем сессию: {session_id} ({len(messages)} сообщений)"))
    elif "--delete" in flags:
        rest = [a for a in args if a != "--delete"]
        if not rest:
            print(error("Укажи id сессии: termucoder chat --delete <id>"))
            return
        if history_mod.delete_session(rest[0]):
            print(ok(f"Сессия удалена: {rest[0]}"))
        else:
            print(error("Сессия не найдена"))
        return
    elif "--list" in flags:
        sessions = history_mod.list_sessions()
        if not sessions:
            print(note("Нет сохранённых сессий"))
            return
        print(header("Сохранённые сессии:"))
        for s in sessions:
            print(f"  - {s}")
        return
    else:
        session_id = history_mod.latest_session() or history_mod.new_session_id()
        messages = history_mod.load_session(session_id)
        if messages:
            print(ok(f"Продолжаем последнюю сессию: {session_id}"))
        else:
            print(ok(f"Новая сессия: {session_id}"))

    print(muted("Вводи сообщения. /exit — выход, /clear — очистить историю."))
    print()

    client = LLMClient(registry=registry)

    try:
        while True:
            try:
                line = input("you> ").strip()
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                break

            if not line:
                continue

            if line in ("/exit", "/quit"):
                break

            if line == "/clear":
                messages = []
                print(warning("История очищена"))
                continue

            messages.append({"role": "user", "content": line})
            reply = client.chat(messages)
            messages.append({"role": "assistant", "content": reply})
            print("\n")
            history_mod.save_session(session_id, messages)

            if auto_memory:
                _try_extract_memory(client, line, reply)
    finally:
        history_mod.save_session(session_id, messages)
        print(muted(f"Сессия сохранена: {session_id}"))


def analyze_command(args):
    """Анализ проекта (v0.4)."""
    flags = set(args)
    rest = [a for a in args if not a.startswith("--")]

    path = rest[0] if rest else "."

    if "--json" in flags:
        import json as _json
        info = context_mod.analyze_project(path)
        info.pop("contents", None)
        print(_json.dumps(info, ensure_ascii=False, indent=2))
        return

    if "--ask" in flags:
        idx = args.index("--ask")
        question = " ".join(args[idx + 1:]) if idx + 1 < len(args) else ""
        if not question:
            print(error("Укажи вопрос: termucoder analyze . --ask \"... \""))
            return
        print(header(f"📂 Анализ проекта: {path}"))
        context_text = context_mod.build_prompt(path)
        client = LLMClient()
        client.ask_context(context_text, question)
        print()
        return

    print(header(f"📂 Анализ проекта: {path}"))
    print()
    print(context_mod.summarize(path))



def edit_command(args):
    """AI редактирование файла через diff."""

    flags = set(args)
    rest = [a for a in args if not a.startswith("--")]

    if "--undo" in flags:
        if not rest:
            print(error("Укажи файл: termucoder edit --undo <файл>"))
            return
        try:
            from termucoder.editor import undo_edit
            undo_edit(rest[0])
        except FileNotFoundError as e:
            print(error(str(e)))
        return

    if len(rest) < 2:
        print(error(
            "Использование: termucoder edit [--preview] <файл> \"что изменить\""
        ))
        return

    path = rest[0]
    instruction = " ".join(rest[1:])
    preview = "--preview" in flags

    try:
        edit_file(path, instruction, preview=preview)
    except FileNotFoundError:
        print(error(f"Файл не найден: {path}"))
    except ValueError as e:
        print(error(str(e)))
    except Exception as e:
        print(error(str(e)))



def plugin_command(args):
    """Управление плагинами: list / info."""
    if not args:
        print("\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u043e:\n  termucoder plugin list\n  termucoder plugin info")
        return

    action = args[0]

    if action == "list":
        registry = PluginRegistry()
        loaded = load_plugins(registry)
        if not loaded:
            print(note("Плагины не найдены"))
            return
        print(header(f"Загружено плагинов: {len(loaded)}"))
        print()
        for p in loaded:
            print(f"  {p['name']} v{p['version']}")
            if p.get('description'):
                print(f"    {p['description']}")
        return

    if action == "info":
        print(header("Плагины:"))
        print()
        print("Директории поиска:")
        from termucoder.plugins.loader import PLUGIN_DIRS
        for d in PLUGIN_DIRS:
            exists = "✓" if __import__("os").path.isdir(d) else "✗"
            print(f"  {exists} {d}")
        print()
        print("Создай плагин:")
        print("  ~/.termucoder/plugins/my_plugin/__init__.py")
        print("  def register(registry):")
        print("      registry.add_command(...)")
        return

    print(error(f"Неизвестная команда plugin: {action}"))

def ask_command(args):
    """Одиночный вопрос модели."""
    prompt = " ".join(args)

    if not prompt:
        print(error("Укажи текст запроса: termucoder ask \"... \""))
        return

    client = LLMClient(registry=registry)
    client.ask(prompt)
    print()


def memory_command(args):
    """Управление памятью проекта: add / list / search / delete / context."""
    if not args:
        print("Использование:\n"
              "  termucoder memory add \"текст\" --tags t1,t2\n"
              "  termucoder memory list\n"
              "  termucoder memory search \"запрос\"\n"
              "  termucoder memory delete <id>\n"
              "  termucoder memory context")
        return

    action = args[0]

    if action == "add":
        if len(args) < 2:
            print(error("Укажи текст: termucoder memory add \"текст\""))
            return
        tags = []
        text_parts = []
        i = 1
        while i < len(args):
            if args[i] == "--tags" and i + 1 < len(args):
                tags = [t.strip() for t in args[i + 1].split(",")]
                i += 2
            else:
                text_parts.append(args[i])
                i += 1
        content = " ".join(text_parts)
        entry = memory_mod.add(content, tags=tags)
        print(ok(f"Запись создана: {entry['id']}"))
        return

    if action == "list":
        entries = memory_mod.list_all()
        if not entries:
            print(note("Память пуста"))
            return
        print(header(f"Память проекта ({len(entries)} записей):"))
        print()
        for e in entries:
            tags = ", ".join(e.get("tags", []))
            tag_str = f" [{tags}]" if tags else ""
            print(f"  {e['id']}{tag_str}")
            print(f"    {e['content']}")
            print()
        return

    if action == "search":
        if len(args) < 2:
            print(error("Укажи запрос: termucoder memory search \"запрос\""))
            return
        query = " ".join(args[1:])
        results = memory_mod.search(query)
        if not results:
            print(note("Ничего не найдено"))
            return
        print(header(f"Найдено {len(results)} записей:"))
        print()
        for e in results:
            print(f"  {e['id']}: {e['content']}")
        return

    if action == "delete":
        if len(args) < 2:
            print(error("Укажи ID: termucoder memory delete <id>"))
            return
        if memory_mod.delete(args[1]):
            print(ok(f"Запись удалена: {args[1]}"))
        else:
            print(error("Запись не найдена"))
        return

    if action == "context":
        ctx = memory_mod.get_context()
        if not ctx:
            print(note("Память пуста"))
            return
        print(header("Контекст для AI:"))
        print()
        print(ctx)
        return

    print(error(f"Неизвестная команда memory: {action}"))


# ---------------------------------------------------------------------------
# Справка
# ---------------------------------------------------------------------------

COMMANDS_HELP = [
    ("ask <текст>",            "Задать модели одиночный вопрос"),
    ("edit <файл>",            "AI правка файла (--preview, --undo)"),
    ("chat",                   "Интерактивный чат (--new, --list, --session, --delete)"),
    ("memory <команда>",      "Память проекта (add/list/search/delete/context)"),
    ("plugin <команда>",      "Плагины (list/info)"),
    ("config",                 "Показать настройки (show/set/init)"),
    ("server <команда>",      "Управление llama-server (start/stop/restart/status)"),
    ("model <команда>",       "Управление моделями (list/info/use)"),
    ("setup [--full]",         "Настройка окружения"),
    ("doctor",                 "Диагностика системы"),
    ("analyze <путь>",         "Анализ проекта (--ask, --json)"),
    ("--version, -v",          "Показать версию"),
    ("--help, -h",             "Показать эту справку"),
]


def print_help():
    from termucoder.utils import bold, dim, separator, success, info

    print(header(f"TermuCoderAI {get_version()}"))
    print(dim("  Локальный AI-ассистент для разработчика"))
    print()
    print(f"  {bold('Использование:')} termucoder <команда> [аргументы]")
    print()

    # Основные команды
    print(f"  {bold('Основные команды:')}")
    for name, desc in [
        ("ask <текст>", "Задать модели вопрос"),
        ("chat", "Интерактивный чат"),
        ("edit <файл>", "AI-правка файла"),
        ("memory", "Память проекта"),
    ]:
        print(f"    {success(name):<30} {dim(desc)}")
    print()

    # Сервер и модель
    print(f"  {bold('Сервер и модель:')}")
    for name, desc in [
        ("server <cmd>", "Управление llama-server"),
        ("model <cmd>", "Управление моделями"),
    ]:
        print(f"    {info(name):<30} {dim(desc)}")
    print()

    # Инструменты
    print(f"  {bold('Инструменты:')}")
    for name, desc in [
        ("analyze <путь>", "Анализ проекта"),
        ("config", "Настройки"),
        ("plugin", "Плагины"),
        ("setup", "Настройка окружения"),
        ("doctor", "Диагностика"),
    ]:
        print(f"    {info(name):<30} {dim(desc)}")
    print()

    print(separator())
    print(dim("  Примеры:"))
    print(f"    termucoder ask \"объясни этот код\"")
    print(f"    termucoder chat")
    print(f"    termucoder edit script.py \"добавь docstring\"")
    print(f"    termucoder memory add \"API использует REST\" --tags api")
    print(f"    termucoder analyze . --ask \"что делает проект?\"")


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

def main():
    setup_completion()

    # Load plugins
    registry = PluginRegistry()
    load_plugins(registry)

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
        "edit": edit_command,
        "chat": chat_command,
        "config": config_command,
        "server": server_command,
        "model": model_command,
        "memory": memory_command,
        "plugin": plugin_command,
        "setup": lambda a: setup("--full" in a, "--start" in a),
        "doctor": lambda a: doctor(),
        "analyze": analyze_command,
    }

    # Register plugin commands
    for name, handler in registry.get_commands().items():
        if name not in handlers:
            handlers[name] = handler

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
