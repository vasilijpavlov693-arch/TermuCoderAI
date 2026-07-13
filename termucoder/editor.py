"""AI редактор кода TermuCoderAI v0.5."""

import os

from termucoder.api import LLMClient
from termucoder.edit_validator import is_valid
from termucoder.search_replace import apply_changes, ReplaceError


def read_file(path):

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()



def build_edit_prompt(code, instruction, filename):

    return f"""
Ты профессиональный AI-редактор кода.

Файл:
{filename}

Задача:
{instruction}

Верни ТОЛЬКО один блок:

SEARCH
<точный существующий текст>

REPLACE
<новый текст>

END

Правила:
- SEARCH обязан существовать в файле.
- SEARCH и REPLACE обязаны отличаться.
- Не возвращай старый текст без изменений.
- Не создавай пустые изменения.
- Меняй только минимально необходимый участок.
- Если задача требует добавления текста, реально добавь новый текст.
- Не переименовывай функции и переменные без запроса.
- Без Markdown.
- Без пояснений.

===== ФАЙЛ =====

{code}

===== КОНЕЦ =====
"""



def build_retry_prompt(error, instruction):

    return f"""

Предыдущий ответ был отклонён.

Причина:
{error}

Исправь только SEARCH/REPLACE.

Требования:
- Верни один блок.
- SEARCH должен отличаться от REPLACE.
- SEARCH должен существовать в файле.
- REPLACE должен выполнять исходную задачу:

{instruction}

Не повторяй предыдущий ответ.

"""



def edit_file(path, instruction):

    code = read_file(path)

    prompt = build_edit_prompt(
        code,
        instruction,
        os.path.basename(path)
    )

    client = LLMClient()

    last_error = None


    for attempt in range(3):

        result = client.ask(prompt)


        if not is_valid(result):

            last_error = (
                "Неверный формат SEARCH/REPLACE"
            )

        else:

            try:

                apply_changes(
                    path,
                    result
                )


                print(
                    "Изменения применены:"
                )

                print(result)

                return


            except ReplaceError as e:

                last_error = str(e)


        prompt = (
            build_edit_prompt(
                code,
                instruction,
                os.path.basename(path)
            )
            +
            build_retry_prompt(
                last_error,
                instruction
            )
        )


    raise Exception(
        f"Не удалось получить корректное изменение: {last_error}"
    )
