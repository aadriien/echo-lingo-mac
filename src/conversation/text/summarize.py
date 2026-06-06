import ollama
from conversation.config import OLLAMA_MODEL
from history.config import SUMMARIZE_PROMPTS


def summarize_conversation(messages: list, language: str) -> list[str]:
    if len(messages) < 2:
        return []
    system = {
        "role": "system",
        "content": SUMMARIZE_PROMPTS.get(language, SUMMARIZE_PROMPTS["English"]),
    }
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[system] + messages)
        raw   = response["message"]["content"]
        lines = [l.strip().lstrip("-•*·").strip() for l in raw.splitlines() if l.strip()]
        return [l for l in lines if l][:5]
    except Exception:
        return []
