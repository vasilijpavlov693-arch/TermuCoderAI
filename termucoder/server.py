import os
import sys
import subprocess
import signal
import time
import shutil

from termucoder.config import load_config

IS_WINDOWS = sys.platform == "win32"
PID_FILE = ".termucoder_server.pid"
LOG_FILE = "llama-server.log"


def _find_llama_server():
    """Найти бинарник llama-server."""
    cfg = load_config()
    server = cfg.get("server", {})

    # Проверяем путь из конфига
    custom = server.get("binary", "")
    if custom:
        path = os.path.expanduser(custom)
        if os.path.isfile(path):
            return path

    # Ищем в стандартных местах
    suffix = ".exe" if IS_WINDOWS else ""
    candidates = []

    if IS_WINDOWS:
        candidates = [
            os.path.expanduser("~/AI/llama.cpp/llama-server.exe"),
            os.path.expanduser("~/AI/llama.cpp/build/bin/Release/llama-server.exe"),
            os.path.expanduser("~/AI/llama.cpp/build/bin/llama-server.exe"),
        ]
    else:
        candidates = [
            os.path.expanduser("~/AI/llama.cpp/build/bin/llama-server"),
            os.path.expanduser("~/AI/llama.cpp/llama-server"),
        ]

    for p in candidates:
        if os.path.isfile(p):
            return p

    # Ищем в PATH
    found = shutil.which(f"llama-server{suffix}")
    if found:
        return found

    return None


def get_command():
    cfg = load_config()
    server = cfg.get("server", {})
    model = cfg.get("model", {})

    binary = _find_llama_server()
    if not binary:
        raise Exception("llama-server не найден. Установи llama.cpp или укажи путь в server.binary")

    model_path = os.path.expanduser(model.get("path", ""))
    if not model_path:
        raise Exception("Путь к модели не указан (настрой model.path)")
    if not os.path.exists(model_path):
        raise Exception(f"Модель не найдена: {model_path}")

    cmd = [
        binary,
        "-m", model_path,
        "-c", str(server.get("context", 2048)),
        "--host", server.get("host", "127.0.0.1"),
        "--port", str(server.get("port", 8080)),
    ]

    if server.get("threads"):
        cmd += ["--threads", str(server["threads"])]
    if server.get("gpu_layers"):
        cmd += ["-ngl", str(server["gpu_layers"])]
    if server.get("parallel"):
        cmd += ["--parallel", str(server["parallel"])]

    return cmd


def get_saved_pid():
    if not os.path.exists(PID_FILE):
        return None
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except (ValueError, OSError):
        return None


def _pid_exists(pid):
    """Проверить существование процесса по PID (кроссплатформенно)."""
    if IS_WINDOWS:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return str(pid) in result.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def _is_llama_pid(pid):
    """Проверить, что PID — это llama-server процесс."""
    if not pid or not _pid_exists(pid):
        return False

    if IS_WINDOWS:
        try:
            result = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "llama-server" in result.stdout.lower()
        except Exception:
            return False
    else:
        try:
            with open(f"/proc/{pid}/cmdline", "r") as f:
                return "llama-server" in f.read()
        except (OSError, IOError):
            return False


def find_existing_server():
    """Найти уже запущенный llama-server."""
    saved = get_saved_pid()
    if _is_llama_pid(saved):
        return saved

    # Ищем через tasklist/wmic на Windows, pgrep на Linux
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ["wmic", "process", "where", "name like '%llama-server%'", "get", "ProcessId"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line.isdigit():
                    pid = int(line)
                    if _is_llama_pid(pid):
                        return pid
        else:
            result = subprocess.check_output(
                ["sh", "-c", "pgrep -f llama-server"], text=True
            )
            for line in result.strip().split("\n"):
                pid = int(line.strip())
                if _is_llama_pid(pid):
                    return pid
    except Exception:
        pass

    return None


def get_running_pid():
    pid = get_saved_pid()
    if _is_llama_pid(pid):
        return pid

    pid = find_existing_server()
    if pid:
        with open(PID_FILE, "w") as f:
            f.write(str(pid))
        return pid

    return None


def is_running():
    return get_running_pid() is not None


def start_server():
    if is_running():
        print(f"  Сервер уже запущен (PID {get_running_pid()})")
        return

    try:
        cmd = get_command()
    except Exception as e:
        print(f"  Ошибка: {e}")
        return

    cfg = load_config()
    server = cfg.get("server", {})
    host = server.get("host", "127.0.0.1")
    port = server.get("port", 8080)
    model = cfg.get("model", {})
    model_name = model.get("name", "?")
    context = server.get("context", 2048)

    print()
    print(f"  Запуск llama-server...")
    print(f"    Модель:    {model_name}")
    print(f"    Контекст:  {context} токенов")
    print(f"    Адрес:     http://{host}:{port}")
    print()

    log = open(LOG_FILE, "w", encoding="utf-8")

    creationflags = 0
    if IS_WINDOWS:
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.Popen(
            cmd, stdout=log, stderr=log,
            creationflags=creationflags
        )
    except Exception as e:
        print(f"  Не удалось запустить: {e}")
        log.close()
        return

    # Ждём запуска — проверяем каждые 0.5с, макс 10с
    started = False
    for _ in range(20):
        time.sleep(0.5)
        if process.poll() is not None:
            break
        # Проверяем лог — llama-server пишет "address" когда готов
        try:
            log.seek(0)
            content = log.read()
            if "address" in content.lower() or "listening" in content.lower():
                started = True
                break
        except Exception:
            pass

    if process.poll() is not None:
        print("  llama-server завершился при запуске. Проверь llama-server.log")
        log.close()
        return

    if not started:
        # Если не нашли ключевое слово в логе, даём ещё шанс
        time.sleep(2)
        if process.poll() is not None:
            print("  llama-server завершился. Проверь llama-server.log")
            log.close()
            return
        started = True

    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"  Сервер запущен! (PID {process.pid})")
    print(f"  API доступен: http://{host}:{port}/v1/chat/completions")
    print(f"  Лог: llama-server.log")
    print()


def stop_server():
    pid = get_running_pid()
    if not pid:
        print("  Сервер не запущен")
        return

    try:
        if IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"  Сервер остановлен (PID {pid})")
    except Exception:
        print("  Не удалось остановить процесс")

    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def restart_server():
    print("  Перезапуск сервера...")
    stop_server()
    time.sleep(2)
    start_server()


def status_server():
    pid = get_running_pid()
    if pid:
        cfg = load_config()
        server = cfg.get("server", {})
        host = server.get("host", "127.0.0.1")
        port = server.get("port", 8080)
        print(f"  Сервер работает (PID {pid})")
        print(f"  API: http://{host}:{port}/v1/chat/completions")
    else:
        print("  Сервер не запущен")
        print(f"  Запуск: termucoder server start")
