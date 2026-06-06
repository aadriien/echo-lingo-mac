import json
from pathlib import Path

HISTORY_DIR = Path(__file__).parent / "json"
MAX_BULLETS = 15


def _path(topic_name: str, language: str) -> Path:
    safe = topic_name.lower().replace(" ", "_").replace("&", "and")
    return HISTORY_DIR / f"{safe}_{language.lower()}.json"


def load_bullets(topic_name: str, language: str) -> list[str]:
    path = _path(topic_name, language)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("bullets", [])
    except Exception:
        return []


def save_bullets(topic_name: str, language: str, new_bullets: list[str]):
    if not new_bullets:
        return
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_bullets(topic_name, language)
    trimmed  = (existing + new_bullets)[-MAX_BULLETS:]  # FIFO: keep most recent
    with open(_path(topic_name, language), "w", encoding="utf-8") as f:
        json.dump({"bullets": trimmed}, f, ensure_ascii=False, indent=2)
