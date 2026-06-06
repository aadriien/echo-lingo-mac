###############################################################################
##  `text_to_text.py`                                                        ##
##                                                                           ##
##  Purpose: LLM responses via local Mistral (Ollama)                       ##
###############################################################################


import ollama
from conversation.config import OLLAMA_MODEL


_TONE = (
    "Keep your reply proportional to what the user said — "
    "a short message gets a short reply, not an essay. "
    "Sound like a real person having a natural back-and-forth, not a teacher giving a lesson."
)

SYSTEM_PROMPTS = {
    "English": f"You are a friendly conversational partner. Reply in clear, casual English. {_TONE}",
    "Spanish": f"Eres un compañero de conversación amigable. Responde en español claro y casual. {_TONE}",
    "French":  f"Tu es un partenaire de conversation amical. Réponds en français clair et naturel. {_TONE}",
    "German":  f"Du bist ein freundlicher Gesprächspartner. Antworte in klarem, lockerem Deutsch. {_TONE}",
}


def get_chat_response(messages, language="Spanish"):
    # messages: full conversation history as list of {"role": ..., "content": ...}
    system = {"role": "system", "content": SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["English"])}

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[system] + messages,
        )
        return response["message"]["content"]

    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")


def stream_chat_response(messages, language="Spanish"):
    """Yield text chunks as the model streams them."""
    system = {"role": "system", "content": SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["English"])}
    try:
        for part in ollama.chat(
            model=OLLAMA_MODEL,
            messages=[system] + messages,
            stream=True,
        ):
            chunk = part.get("message", {}).get("content", "")
            if chunk:
                yield chunk
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error ({e.status_code}): {e.error}")
    except Exception as e:
        raise RuntimeError(f"Failed to reach Ollama. Is it running? ({e})")