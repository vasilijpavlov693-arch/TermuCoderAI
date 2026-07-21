"""Подсчёт токенов для TermuCoderAI.

Использует эвристический подсчёт: ~4 символа на токен для латиницы,
~2 символа на токен для кириллицы и кода.
"""

import re

LATIN_RATIO = 4.0
CYRILLIC_RATIO = 2.5
CODE_RATIO = 3.5


def _char_type_ratio(text):
    if not text:
        return LATIN_RATIO
    total = len(text)
    cyrillic = len(re.findall(r"[а-яА-ЯёЁ]", text))
    cyrillic_pct = cyrillic / total if total else 0
    if cyrillic_pct > 0.3:
        return CYRILLIC_RATIO
    elif cyrillic_pct > 0.05:
        return LATIN_RATIO * (1 - cyrillic_pct) + CYRILLIC_RATIO * cyrillic_pct
    else:
        return LATIN_RATIO


def count_tokens(text):
    if not text:
        return 0
    ratio = _char_type_ratio(text)
    return max(1, int(len(text) / ratio))


def count_messages_tokens(messages):
    total = 4
    for msg in messages:
        total += count_tokens(msg.get("content", ""))
        total += 4
    return total


def fit_messages_to_context(messages, context_size, max_response=512, system_prompt_tokens=50):
    available = context_size - max_response - system_prompt_tokens
    if available <= 0:
        return messages[-1:] if messages else []
    result = []
    used = 0
    for msg in reversed(messages):
        msg_tokens = count_tokens(msg.get("content", "")) + 4
        if used + msg_tokens > available:
            break
        result.append(msg)
        used += msg_tokens
    result.reverse()
    return result


def summarize_messages(messages, keep_recent=4):
    if len(messages) <= keep_recent:
        return messages
    old = messages[:-keep_recent]
    recent = messages[-keep_recent:]
    summary_parts = []
    for msg in old:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        snippet = content[:100].replace(chr(10), " ")
        if len(content) > 100:
            snippet += "..."
        summary_parts.append(f"{role}: {snippet}")
    summary = "Краткое содержание предыдущего диалога:" + chr(10).join(summary_parts)
    return [{"role": "system", "content": summary}] + recent
