###############################################################################
##  `text_to_text.py`                                                        ##
##                                                                           ##
##  Purpose: LLM responses via local Mistral (Ollama)                       ##
###############################################################################


import ollama
from conversation.config import OLLAMA_MODEL


SYSTEM_PROMPTS = {
    "English": (
        "You're a native English speaker texting a friend. "
        "Keep it casual and natural; short messages get short replies, not essays. "
        "You're not a teacher or tutor, just someone having a normal chat. "
        "Never add translations or parenthetical notes in other languages."
    ),
    "Spanish": (
        "Eres un hablante nativo de español chateando con un amigo. "
        "Escribe de forma casual y natural, como en una conversación de texto real. Los mensajes cortos reciben respuestas cortas, no ensayos. "
        "No eres un profesor ni un tutor, solo alguien teniendo una charla normal. "
        "Nunca añadas traducciones ni notas entre paréntesis en ningún otro idioma."
    ),
    "French": (
        "Tu es un francophone natif qui chatte avec un ami. "
        "Écris de façon décontractée et naturelle, comme dans une vraie conversation par texto. Les messages courts reçoivent des réponses courtes, pas des dissertations. "
        "Tu n'es pas un professeur ni un tuteur, juste quelqu'un qui discute normalement. "
        "N'ajoute jamais de traductions ni de notes entre parenthèses dans une autre langue."
    ),
    "German": (
        "Du bist ein Muttersprachler, der mit einem Freund chattet. "
        "Schreib locker und natürlich, wie in einer echten Textnachricht. Kurze Nachrichten bekommen kurze Antworten, keine Aufsätze. "
        "Du bist kein Lehrer und kein Tutor, nur jemand der normal plaudert. "
        "Füge niemals Übersetzungen oder Anmerkungen in Klammern in einer anderen Sprache hinzu."
    ),
}


def _build_system(language: str, messages: list) -> str:
    base = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["English"])
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    word_target = max(20, min(80, len(last_user.split()) * 2))
    return f"{base} Reply in at most {word_target} words."


def get_chat_response(messages, language="Spanish"):
    system = {"role": "system", "content": _build_system(language, messages)}
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[system] + messages)
        return response["message"]["content"]
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")


def stream_chat_response(messages, language="Spanish"):
    """Yield text chunks as the model streams them."""
    system = {"role": "system", "content": _build_system(language, messages)}
    try:
        for part in ollama.chat(model=OLLAMA_MODEL, messages=[system] + messages, stream=True):
            chunk = part.get("message", {}).get("content", "")
            if chunk:
                yield chunk
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")