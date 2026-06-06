import ollama
from conversation.config import OLLAMA_MODEL
from history.config import SUMMARIZE_PROMPTS


def summarize_conversation(messages: list, language: str) -> list[str]:
    if len(messages) < 2:
        return []

    # Flatten the full conversation into a single block so the model reads
    # it as text to extract from, not as a chat to continue.
    transcript = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in messages
    )
    payload = [
        {"role": "system",  "content": SUMMARIZE_PROMPTS.get(language, SUMMARIZE_PROMPTS["English"])},
        {"role": "user",    "content": transcript},
    ]
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=payload)
        raw   = response["message"]["content"]
        lines = [l.strip().lstrip("-•*·").strip() for l in raw.splitlines() if l.strip()]
        return [l for l in lines if l][:5]
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to summarize. Is Ollama running? ({e})")
