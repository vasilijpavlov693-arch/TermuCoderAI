"""Анализ проекта и построение контекста для AI (v0.4).

Формирует представление проекта:
  - структуру файлов (дерево);
  - содержимое документации (README и т.п.);
  - содержимое текстовых файлов (с ограничением размера);
  - итоговый промпт для передачи модели.
"""

import functools
import os

from termucoder.search import scan_project, count_by_ext


# Файлы, которые считаем документацией проекта.
DOC_NAMES = {
    "readme.md", "readme.txt", "readme", "readme.rst",
    "changelog.md", "changelog.txt", "license", "license.md",
}

# Расширения текстовых файлов, попадающих в контекст.
TEXT_EXT = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".go", ".rs", ".rb", ".php", ".md", ".txt", ".json", ".yaml",
    ".yml", ".toml", ".sh", ".bat", ".ps1", ".html", ".css", ".sql",
    ".xml", ".ini", ".cfg", ".env.example",
}


def build_structure(root: str, files: "list[str]") -> str:
    """Строит текстовое дерево файлов проекта."""
    tree: dict = {}

    for f in files:
        node = tree
        for part in f.split("/"):
            node = node.setdefault(part, {})

    lines: "list[str]" = []

    def render(node: dict, prefix: str = ""):
        items = sorted(node.keys())

        for i, key in enumerate(items):
            last = i == len(items) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + key)
            render(node[key], prefix + ("    " if last else "│   "))

    render(tree)

    return "\n".join(lines)


def read_docs(root: str, files: "list[str]") -> str:
    """Читает содержимое файлов документации проекта."""
    blocks: "list[str]" = []

    for f in files:
        base = os.path.basename(f).lower()

        in_docs_dir = f.lower().startswith("docs/")

        if base not in DOC_NAMES and not in_docs_dir:
            continue

        try:
            with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                blocks.append(f"# {f}\n\n{fh.read()}")
        except OSError:
            pass

    return "\n\n".join(blocks)


@functools.lru_cache(maxsize=32)
def analyze_project(root: str = ".", max_file_chars: int = 4000, max_files: int = 20) -> dict:
    """Анализирует проект и возвращает словарь с контекстом.

    Ключи: files, structure, docs, contents, stats.
    ``max_files`` ограничивает число загружаемых файлов содержимого, чтобы
    не переполнять память/контекст модели на крупных проектах.
    """
    files = scan_project(root)
    structure = build_structure(root, files)
    docs = read_docs(root, files)

    contents: "dict[str, str]" = {}
    loaded = 0

    for f in files:
        if loaded >= max_files:
            break

        ext = os.path.splitext(f)[1].lower()

        if ext not in TEXT_EXT:
            continue

        try:
            with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                data = fh.read()
        except OSError:
            continue

        if len(data) > max_file_chars:
            data = data[:max_file_chars] + "\n... (обрезано)"

        contents[f] = data
        loaded += 1

    return {
        "files": files,
        "structure": structure,
        "docs": docs,
        "contents": contents,
        "stats": count_by_ext(files),
    }


def build_prompt(root: str = ".") -> str:
    """Формирует итоговый текстовый контекст проекта для отправки модели."""
    info = analyze_project(root)

    parts: "list[str]" = []
    parts.append("Структура проекта:")
    parts.append(info["structure"])

    if info["docs"]:
        parts.append("\nДокументация проекта:")
        parts.append(info["docs"])

    if info["contents"]:
        parts.append("\nСодержимое файлов:")
        for f, content in info["contents"].items():
            parts.append(f"\n--- {f} ---\n{content}")

    return "\n".join(parts)


def summarize(root: str = ".") -> str:
    """Краткое человекочитаемое описание проекта."""
    info = analyze_project(root)
    lines = [
        f"Файлов всего: {len(info['files'])}",
        "По типам:",
    ]

    for ext, count in sorted(info["stats"].items(), key=lambda x: -x[1]):
        lines.append(f"  {ext}: {count}")

    lines.append("")
    lines.append("Структура:")
    lines.append(info["structure"])

    return "\n".join(lines)
