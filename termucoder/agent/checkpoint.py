"""Agent Checkpoint — автосохранение состояния агента."""
import json
import os
import time


CHECKPOINT_DIR = os.path.join(".termucoder", "agent_checkpoints")


def _ensure_dir():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)


def _checkpoint_path(session_id: str) -> str:
    return os.path.join(CHECKPOINT_DIR, session_id + ".json")


def save_checkpoint(session_id: str, task: str, history: list, context: str, step: int):
    """Сохраняет текущее состояние агента."""
    _ensure_dir()
    path = _checkpoint_path(session_id)

    data = {
        "session_id": session_id,
        "task": task,
        "history": history,
        "context": context,
        "step": step,
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_checkpoint(session_id: str) -> dict:
    """Загружает состояние агента. Возвращает {} если не найдено."""
    path = _checkpoint_path(session_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_checkpoints() -> list:
    """Возвращает список сохранённых чекпоинтов."""
    if not os.path.isdir(CHECKPOINT_DIR):
        return []
    return sorted([
        f.replace(".json", "")
        for f in os.listdir(CHECKPOINT_DIR)
        if f.endswith(".json")
    ])


def delete_checkpoint(session_id: str) -> bool:
    """Удаляет чекпоинт."""
    path = _checkpoint_path(session_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
