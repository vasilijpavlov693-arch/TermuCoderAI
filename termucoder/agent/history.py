"""Agent History — лог действий агента для отладки и аудита."""
import json
import os
import time


HISTORY_DIR = os.path.join(".termucoder", "agent_history")


def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _session_path(session_id: str) -> str:
    return os.path.join(HISTORY_DIR, session_id + ".json")


def new_session_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def log_action(session_id: str, step: int, action: dict, result: str):
    """Логирует одно действие агента."""
    _ensure_dir()
    path = _session_path(session_id)

    entry = {
        "step": step,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "action": action,
        "result": result[:500],
    }

    # Load existing or create new
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"session_id": session_id, "actions": []}

    data["actions"].append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_done(session_id: str, result: str):
    """Логирует завершение задачи."""
    _ensure_dir()
    path = _session_path(session_id)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"session_id": session_id, "actions": []}

    data["completed"] = True
    data["result"] = result
    data["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_session(session_id: str) -> dict:
    """Возвращает лог сессии."""
    path = _session_path(session_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sessions() -> list:
    """Возвращает список всех сессий."""
    if not os.path.isdir(HISTORY_DIR):
        return []
    return sorted([
        f.replace(".json", "")
        for f in os.listdir(HISTORY_DIR)
        if f.endswith(".json")
    ])


def format_session(session_id: str) -> str:
    """Форматирует лог сессии для вывода."""
    data = get_session(session_id)
    if not data:
        return "Сессия не найдена"

    lines = [f"Session: {session_id}"]
    lines.append(f"Completed: {data.get('completed', False)}")
    lines.append(f"Result: {data.get('result', 'N/A')}")
    lines.append("")

    for entry in data.get("actions", []):
        action = entry.get("action", {})
        tool = action.get("tool", "?")
        lines.append(f"  Step {entry['step']}: {tool}")

    return chr(10).join(lines)
