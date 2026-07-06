from termucoder.api import LLMClient
from termucoder.config import (
    load_config,
    save_config,
    init_config
)


def config_command(args):

    if len(args) == 0:

        cfg = load_config()

        print()

        print("⚙ TermuCoderAI config:")
        print()

        for section, values in cfg.items():

            print(
                f"[{section}]"
            )

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



def main():

    import sys


    if len(sys.argv) < 2:

        print(
            "Использование:\n"
            "termucoder ask <текст>\n"
            "termucoder code <текст>\n"
            "termucoder config"
        )

        return



    command = sys.argv[1]


    if command == "config":

        config_command(
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
