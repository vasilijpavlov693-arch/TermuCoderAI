"""Проверка корректности SEARCH/REPLACE."""

import re


def is_valid(response: str):

    if "SEARCH" not in response:
        return False

    if "REPLACE" not in response:
        return False


    # Запрещаем Markdown-ответы
    if "```" in response:
        return False


    # Слишком большие ответы почти всегда означают полный файл
    if len(response) > 5000:
        return False


    blocks = re.findall(
        r"SEARCH\s*(.*?)\s*REPLACE\s*(.*?)\s*END",
        response,
        re.S
    )


    if len(blocks) < 1:
        return False


    search, replace = blocks[0]


    search = search.strip()
    replace = replace.strip()


    if not search or not replace:
        return False


    if search == replace:
        return False


    # SEARCH должен быть больше одного слова
    if (
        len(search.splitlines()) == 1
        and len(search.split()) == 1
    ):
        return False


    # REPLACE не должен превращаться в полный файл
    if len(replace) > len(search) * 20:
        return False


    return True
