"""AI редактор кода TermuCoderAI v0.5."""

import os

from termucoder.api import LLMClient
from termucoder.diff import create_diff
from termucoder.edit_validator import is_valid
from termucoder.search_replace import apply_changes, parse_blocks, ReplaceError

MAX_FILE_SIZE = 100_000


def read_file(path):

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise ValueError(
            f"Файл слишком большой ({size} байт). "
            f"Лимит: {MAX_FILE_SIZE} байт."
        )

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:
        return f.read()



def build_edit_prompt(code, instruction, filename):

    return f"""
Ты профессиональный AI-редактор кода.

Файл:
{filename}

Задача:
{instruction}

Верни ТОЛЬКО блок(и):

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
- Верни блок(и).
- SEARCH должен отличаться от REPLACE.
- SEARCH должен существовать в файле.
- REPLACE должен выполнять исходную задачу:

{instruction}

Не повторяй предыдущий ответ.

"""



def edit_file(path, instruction, preview=False):

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

            blocks = parse_blocks(result)

            if not blocks:
                last_error = "Нет полезных блоков"
            else:
                new_content = code
                for search, replace in blocks:
                    new_content = new_content.replace(search, replace, 1)

                diff = create_diff(code, new_content, os.path.basename(path))

                if not diff:
                    last_error = "Файл не изменился"
                elif preview:
                    print("Предпросмотр изменений:\n")
                    print(diff)
                    print("\nФайл не изменён (режим --preview).")
                    return {"preview": True, "diff": diff}
                else:
                    apply_changes(path, result)
                    print("Изменения применены:\n")
                    print(diff)
                    return {"preview": False, "diff": diff}


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


def undo_edit(path):
    """Восстанавливает файл из .bak резервной копии."""
    file = os.path.abspath(path)
    bak = file + ".bak"

    if not os.path.exists(bak):
        raise FileNotFoundError(
            f"Резервная копия не найдена: {bak}"
        )

    import shutil
    shutil.copy2(bak, file)
    os.remove(bak)

    print(f"Файл восстановлен из {os.path.basename(bak)}")
