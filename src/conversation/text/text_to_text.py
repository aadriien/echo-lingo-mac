###############################################################################
##  `text_to_text.py`                                                        ##
##                                                                           ##
##  Purpose: LLM responses via local Mistral (Ollama)                        ##
###############################################################################


import ollama
from conversation.config import OLLAMA_MODEL
from conversation.text.config import SYSTEM_PROMPTS, TOPIC_PROMPTS
from topics.config import topic_hint


def _build_system(language: str, messages: list, topic: dict | None = None) -> str:
    base = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["English"])
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    word_target = max(20, min(80, len(last_user.split()) * 2))
    hint = topic_hint(topic, language) if topic else None
    if hint:
        template = TOPIC_PROMPTS.get(language, TOPIC_PROMPTS["English"])
        topic_ctx = " " + template.format(hint=hint)
    else:
        topic_ctx = ""
    return f"{base}{topic_ctx} Reply in at most {word_target} words."


def get_chat_response(messages, language="Spanish", topic=None):
    system = {"role": "system", "content": _build_system(language, messages, topic)}
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[system] + messages)
        return response["message"]["content"]
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")


def stream_chat_response(messages, language="Spanish", topic=None):
    """Yield text chunks as the model streams them."""
    system = {"role": "system", "content": _build_system(language, messages, topic)}
    try:
        for part in ollama.chat(model=OLLAMA_MODEL, messages=[system] + messages, stream=True):
            chunk = part.get("message", {}).get("content", "")
            if chunk:
                yield chunk
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")