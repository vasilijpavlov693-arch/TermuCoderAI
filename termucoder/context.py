"""Анализ проекта и построение контекста для AI (v0.4)."""

import os

from termucoder.search import scan_project, count_by_ext


DOC_NAMES = {
    "readme.md", "readme.txt", "readme", "readme.rst",
    "changelog.md", "changelog.txt", "license", "license.md",
}

TEXT_EXT = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".go", ".rs", ".rb", ".php", ".md", ".txt", ".json", ".yaml",
    ".yml", ".toml", ".sh", ".bat", ".ps1", ".html", ".css", ".sql",
    ".xml", ".ini", ".cfg", ".env.example",
}

PRIORITY_PREFIXES = ("termucoder/", "tests/")


def _sort_key(path):
    for i, prefix in enumerate(PRIORITY_PREFIXES):
        if path.startswith(prefix):
            return (i, path)
    return (len(PRIORITY_PREFIXES), path)


def build_structure(root, files):
    tree = {}
    for f in files:
        node = tree
        for part in f.split("/"):
            node = node.setdefault(part, {})

    lines = []

    def render(node, prefix=""):
        items = sorted(node.keys())
        for i, key in enumerate(items):
            last = i == len(items) - 1
            branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
            lines.append(prefix + branch + key)
            render(node[key], prefix + ("    " if last else "\u2502   "))

    render(tree)
    return "\n".join(lines)


def read_docs(root, files):
    blocks = []
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


def analyze_project(root=".", max_file_chars=4000, max_files=40):
    files = scan_project(root)
    structure = build_structure(root, files)
    docs = read_docs(root, files)

    sorted_files = sorted(files, key=_sort_key)

    contents = {}
    loaded = 0

    for f in sorted_files:
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
            data = data[:max_file_chars] + "\n... (\u043e\u0431\u0440\u0435\u0437\u0430\u043d\u043e)"

        contents[f] = data
        loaded += 1

    return {
        "files": files,
        "structure": structure,
        "docs": docs,
        "contents": contents,
        "stats": count_by_ext(files),
    }


def build_prompt(root="."):
    from termucoder import memory as memory_mod
    from termucoder.config import load_config

    info = analyze_project(root)
    parts = []
    parts.append("\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043f\u0440\u043e\u0435\u043a\u0442\u0430:")
    parts.append(info["structure"])

    if info["docs"]:
        parts.append("\n\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f \u043f\u0440\u043e\u0435\u043a\u0442\u0430:")
        parts.append(info["docs"])

    if info["contents"]:
        parts.append("\n\u0421\u043e\u0434\u0435\u0440\u0436\u0438\u043c\u043e\u0435 \u0444\u0430\u0439\u043b\u043e\u0432:")
        for f, content in info["contents"].items():
            parts.append(f"\n--- {f} ---\n{content}")

    cfg = load_config()
    mem_cfg = cfg.get("memory", {})
    if mem_cfg.get("enabled", True):
        limit = mem_cfg.get("context_limit", 10)
        knowledge = memory_mod.get_context(max_entries=limit)
        if knowledge:
            parts.append("\n\u0421\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0435 \u0437\u043d\u0430\u043d\u0438\u044f \u043e \u043f\u0440\u043e\u0435\u043a\u0442\u0435:")
            parts.append(knowledge)

    return "\n".join(parts)


def summarize(root="."):
    info = analyze_project(root)
    lines = [
        f"\u0424\u0430\u0439\u043b\u043e\u0432 \u0432\u0441\u0435\u0433\u043e: {len(info['files'])}",
        "\u041f\u043e \u0442\u0438\u043f\u0430\u043c:",
    ]
    for ext, count in sorted(info["stats"].items(), key=lambda x: -x[1]):
        lines.append(f"  {ext}: {count}")
    lines.append("")
    lines.append("\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430:")
    lines.append(info["structure"])
    return "\n".join(lines)
