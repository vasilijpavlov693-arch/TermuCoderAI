from termucoder.api import LLMClient
import sys


def main():

    if len(sys.argv) < 3:
        print("Использование:")
        print("  termucoder ask \"вопрос\"")
        print("  termucoder code \"запрос кода\"")
        return


    mode = sys.argv[1]
    prompt = " ".join(sys.argv[2:])


    client = LLMClient()


    if mode == "code":

        prompt = (
            "Напиши только код. "
            "Без объяснений, без текста до и после, без Markdown. "
            "Запрос: "
            + prompt
        )

    elif mode == "ask":

        prompt = (
            "Ответь на вопрос пользователя кратко и понятно. "
            "Не повторяй запрос. "
            + prompt
        )

    else:
        print("Неизвестный режим:", mode)
        return


    print("\n🤖 AI:\n")
    client.ask(prompt)


if __name__ == "__main__":
    main()
