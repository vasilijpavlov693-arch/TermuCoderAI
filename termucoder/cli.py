from termucoder.api import LLMClient
from termucoder.config import (
    load_config,
    save_config,
    init_config
)

from termucoder.server import (
    start_server,
    stop_server,
    status_server,
    restart_server
)

from termucoder.doctor import doctor

from termucoder.model import (
    list_models,
    info_model,
    use_model
)



def config_command(args):

    if len(args) == 0:

        cfg = load_config()

        print()
        print("⚙ TermuCoderAI config:")
        print()

        for section, values in cfg.items():

            print(f"[{section}]")

            if isinstance(values, dict):

                for k, v in values.items():

                    print(
                        f"{k} = {v}"
                    )

            else:

                print(values)

            print()

        return


    if args[0] == "init":

        init_config()
        return


    if args[0] == "set":

        if len(args) < 3:

            print(
                "Использование: "
                "termucoder config set section.key value"
            )

            return


        key = args[1]
        value = args[2]

        cfg = load_config()

        parts = key.split(".")


        if len(parts) != 2:

            print(
                "Формат: section.key"
            )

            return


        section, name = parts


        if section not in cfg:

            cfg[section] = {}


        try:

            if value.isdigit():

                value = int(value)

            else:

                value = float(value)

        except:

            pass


        cfg[section][name] = value

        save_config(cfg)

        print(
            "✅ Настройка изменена"
        )



def server_command(args):

    if len(args) == 0:

        print(
            "Использование:\n"
            "termucoder server start\n"
            "termucoder server stop\n"
            "termucoder server restart\n"
            "termucoder server status"
        )

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

        print(
            "Неизвестная команда сервера"
        )



def model_command(args):

    if len(args) == 0:

        print(
            "Использование:\n"
            "termucoder model list\n"
            "termucoder model info\n"
            "termucoder model use <name>"
        )

        return


    action = args[0]


    if action == "list":

        list_models()


    elif action == "info":

        info_model()


    elif action == "use":

        if len(args) < 2:

            print(
                "Укажи имя модели"
            )

            return


        use_model(
            args[1]
        )


    else:

        print(
            "Неизвестная команда модели"
        )



def main():

    import sys


    if len(sys.argv) < 2:

        print(
            "Использование:\n"
            "termucoder ask <текст>\n"
            "termucoder config\n"
            "termucoder server <команда>\n"
            "termucoder model <команда>"
        )

        return


    command = sys.argv[1]


    if command == "config":

        config_command(
            sys.argv[2:]
        )

        return


    if command == "server":

        server_command(
            sys.argv[2:]
        )

        return


    if command == "doctor":

        doctor()

        return


    if command == "model":

        model_command(
            sys.argv[2:]
        )

        return


    prompt = " ".join(
        sys.argv[2:]
    )


    print(
        "\n🤖 AI:\n"
    )


    client = LLMClient()

    client.ask(prompt)



if __name__ == "__main__":

    main()
