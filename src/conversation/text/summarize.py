import re
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
        lines = [re.sub(r'^\d+[.)]\s*', '', line.strip().lstrip("-•*·")).strip()
                 for line in raw.splitlines() if line.strip()]
        return [line for line in lines if line][:4]
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")


def summarize_conversation(messages: list, language: str) -> list[str]:
    # Only extract from what the user said. Assistant replies reflect the LLM's
    # persona, not the user's actual preferences or interests.
    user_msgs = [m for m in messages if m["role"] == "user"]
    if len(user_msgs) < 1:
        return []

    extract_prompt = SUMMARIZE_PROMPTS.get(language, SUMMARIZE_PROMPTS["English"])

    if len(user_msgs) <= _DIRECT_MSG_LIMIT:
        return _call_model(extract_prompt, _flatten(user_msgs))

    # Map: summarize each chunk of user messages independently
    all_bullets: list[str] = []
    for i in range(0, len(user_msgs), _CHUNK_SIZE):
        chunk   = user_msgs[i:i + _CHUNK_SIZE]
        bullets = _call_model(extract_prompt, _flatten(chunk))
        all_bullets.extend(bullets)

    if not all_bullets:
        return []

    # Reduce: condense all intermediate bullets down to 3-5 key points
    reduce_prompt = REDUCE_PROMPTS.get(language, REDUCE_PROMPTS["English"])
    return _call_model(reduce_prompt, "\n".join(all_bullets))
