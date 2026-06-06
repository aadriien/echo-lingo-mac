import ollama
from conversation.config import OLLAMA_MODEL
from history.config import SUMMARIZE_PROMPTS, REDUCE_PROMPTS

_DIRECT_MSG_LIMIT = 16   # summarize in one pass if at or below this many messages
_CHUNK_SIZE       = 8    # messages per chunk during the map phase


def _flatten(messages: list) -> str:
    return "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in messages
    )


def _call_model(system_content: str, user_content: str) -> list[str]:
    payload = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": user_content},
    ]
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=payload)
        raw   = response["message"]["content"]
        lines = [l.strip().lstrip("-•*·").strip() for l in raw.splitlines() if l.strip()]
        return [l for l in lines if l][:5]
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")


def summarize_conversation(messages: list, language: str) -> list[str]:
    if len(messages) < 2:
        return []

    extract_prompt = SUMMARIZE_PROMPTS.get(language, SUMMARIZE_PROMPTS["English"])

    if len(messages) <= _DIRECT_MSG_LIMIT:
        return _call_model(extract_prompt, _flatten(messages))

    # Map: summarize each chunk of messages independently
    all_bullets: list[str] = []
    for i in range(0, len(messages), _CHUNK_SIZE):
        chunk   = messages[i:i + _CHUNK_SIZE]
        bullets = _call_model(extract_prompt, _flatten(chunk))
        all_bullets.extend(bullets)

    if not all_bullets:
        return []

    # Reduce: condense all intermediate bullets down to 3-5 key points
    reduce_prompt = REDUCE_PROMPTS.get(language, REDUCE_PROMPTS["English"])
    return _call_model(reduce_prompt, "\n".join(all_bullets))
