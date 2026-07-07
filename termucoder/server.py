import os
import subprocess
import signal
import json
import time

from termucoder.config import load_config, CONFIG_FILE

PID_FILE = ".termucoder_server.pid"
LOG_FILE = "llama-server.log"


def get_command():

    cfg = load_config()

    server = cfg.get(
        "server",
        {}
    )

    model = cfg.get(
        "model",
        {}
    )


    model_path = os.path.expanduser(
        model.get(
            "path",
            ""
        )
    )


    if not model_path:

        raise Exception(
            "Путь к модели не указан"
        )


    if not os.path.exists(model_path):

        raise Exception(
            f"Модель не найдена: {model_path}"
        )


    cmd = [

        os.path.expanduser(
            "~/AI/llama.cpp/build/bin/llama-server"
        ),

        "-m",
        model_path,

        "-c",
        str(
            server.get(
                "context",
                2048
            )
        ),

        "--host",
        server.get(
            "host",
            "127.0.0.1"
        ),

        "--port",
        str(
            server.get(
                "port",
                8080
            )
        )
    ]


    if server.get("threads"):

        cmd += [
            "--threads",
            str(
                server["threads"]
            )
        ]


    if server.get("gpu_layers"):

        cmd += [
            "-ngl",
            str(
                server["gpu_layers"]
            )
        ]


    if server.get("parallel"):

        cmd += [
            "--parallel",
            str(
                server["parallel"]
            )
        ]


    return cmd



def get_saved_pid():

    if not os.path.exists(PID_FILE):

        return None


    try:

        with open(PID_FILE) as f:

            return int(
                f.read()
            )

    except:

        return None



def process_name(pid):

    try:

        with open(
            f"/proc/{pid}/cmdline",
            "r"
        ) as f:

            return f.read()

    except:

        return ""



def is_llama_process(pid):

    if not pid:

        return False


    name = process_name(pid)


    return (
        "llama-server" in name
    )



def find_existing_server():

    try:

        result = subprocess.check_output(
            [
                "sh",
                "-c",
                "pgrep -f llama-server"
            ],
            text=True
        )


        pid = int(
            result.strip().split("\n")[0]
        )


        if is_llama_process(pid):

            return pid


    except:

        pass


    return None



def get_running_pid():

    pid = get_saved_pid()


    if is_llama_process(pid):

        return pid


    pid = find_existing_server()


    if pid:

        with open(
            PID_FILE,
            "w"
        ) as f:

            f.write(
                str(pid)
            )


        return pid


    return None



def is_running():

    return (
        get_running_pid()
        is not None
    )



def start_server():

    if is_running():

        print(
            f"⚠ Сервер уже запущен PID {get_running_pid()}"
        )

        return


    try:

        cmd = get_command()

    except Exception as e:

        print(
            "❌",
            e
        )

        return


    print(
        "🚀 Запуск llama-server..."
    )


    log = open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    )


    process = subprocess.Popen(
        cmd,
        stdout=log,
        stderr=log
    )


    time.sleep(5)


    if process.poll() is not None:

        print(
            "❌ llama-server завершился"
        )

        log.close()

        return


    with open(
        PID_FILE,
        "w"
    ) as f:

        f.write(
            str(process.pid)
        )


    print(
        f"✅ Сервер запущен PID {process.pid}"
    )



def stop_server():

    pid = get_running_pid()


    if not pid:

        print(
            "⚠ Сервер не найден"
        )

        return


    try:

        os.kill(
            pid,
            signal.SIGTERM
        )

        print(
            "🛑 Сервер остановлен"
        )


    except:

        print(
            "⚠ Не удалось остановить процесс"
        )


    if os.path.exists(PID_FILE):

        os.remove(PID_FILE)



def restart_server():

    print(
        "🔄 Перезапуск..."
    )

    stop_server()

    time.sleep(2)

    start_server()



def status_server():

    pid = get_running_pid()


    if pid:

        print(
            f"✅ Сервер работает PID {pid}"
        )

    else:

        print(
            "❌ Сервер выключен"
        )
