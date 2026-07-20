"""Применение SEARCH/REPLACE изменений."""

from pathlib import Path


class ReplaceError(Exception):
    pass



def clean_replace(text):

    endings = [
        "===== КОНЕЦ =====",
        "===== ФАЙЛ ====="
    ]

    for end in endings:
        if end in text:
            text = text.split(
                end,
                1
            )[0]

    # "END" как отдельная строка, не как подстрока в коде.
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        if line.strip() == "END":
            break
        cleaned.append(line)
    text = "\n".join(cleaned)

    return text.strip()



def parse_blocks(response):

    blocks = []

    parts = response.split("SEARCH")


    for part in parts[1:]:

        if "REPLACE" not in part:
            continue


        search, replace = part.split(
            "REPLACE",
            1
        )


        search = search.strip()

        replace = clean_replace(
            replace
        )


        if not search or not replace:
            continue


        if search == replace:
            continue


        blocks.append(
            (
                search,
                replace
            )
        )


    return blocks



def apply_changes(path, response, backup=True):

    file = Path(path)

    if not file.exists():
        raise ReplaceError(
            f"Файл не найден: {path}"
        )


    content = file.read_text(
        encoding="utf-8",
        errors="replace"
    )


    blocks = parse_blocks(response)


    if not blocks:
        raise ReplaceError(
            "Нет полезных SEARCH/REPLACE изменений"
        )


    result = content
    applied = 0


    for search, replace in blocks:


        count = result.count(search)


        if count == 0:
            continue


        if count > 1:
            raise ReplaceError(
                f"SEARCH найден несколько раз: {count}"
            )


        result = result.replace(
            search,
            replace,
            1
        )

        applied += 1


    if applied == 0:
        raise ReplaceError(
            "SEARCH блоки не найдены"
        )


    if result == content:
        raise ReplaceError(
            "Файл не изменился"
        )

    if backup:
        bak = file.with_suffix(file.suffix + ".bak")
        bak.write_text(content, encoding="utf-8")

    file.write_text(
        result,
        encoding="utf-8"
    )


    return {
        "blocks": applied,
        "changed": True,
        "old_content": content,
        "new_content": result
    }
