"""Диагностика системы TermuCoderAI."""

import os
import sys

from termucoder.config import load_config
from termucoder.server import _find_llama_server


def doctor():
    """Проверка состояния системы."""
    issues = []
    ok_count = 0

    if os.path.exists("settings.json"):
        print("  [OK] settings.json")
        ok_count += 1
    else:
        print("  [ERR] settings.json отсутствует")
        issues.append("settings.json")

    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  [OK] Python {ver}")
    ok_count += 1

    binary = _find_llama_server()
    if binary:
        print(f"  [OK] llama-server: {binary}")
        ok_count += 1
    else:
        print("  [ERR] llama-server не найден")
        issues.append("llama-server")

    cfg = load_config()
    model_path = os.path.expanduser(cfg.get("model", {}).get("path", ""))
    if model_path and os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  [OK] Модель: {os.path.basename(model_path)} ({size_mb:.0f} MB)")
        ok_count += 1
    else:
        name = cfg.get("model", {}).get("name", "?")
        print(f"  [ERR] Модель не найдена: {name}")
        issues.append("model")

    if not issues or "llama-server" not in issues:
        try:
            import requests
            host = cfg.get("server", {}).get("host", "127.0.0.1")
            port = cfg.get("server", {}).get("port", 8080)
            r = requests.get(f"http://{host}:{port}/health", timeout=3)
            if r.status_code == 200:
                print("  [OK] llama-server API доступен")
                ok_count += 1
            else:
                print(f"  [WARN] llama-server API вернул {r.status_code}")
        except Exception:
            print("  [WARN] llama-server API недоступен")
    else:
        print("  [WARN] llama-server API недоступен")

    print()
    if issues:
        print(f"  Найдены проблемы: {', '.join(issues)}")
    else:
        print(f"  Все проверки пройдены ({ok_count}/{ok_count})")

    return len(issues) == 0


if __name__ == "__main__":
    doctor()
