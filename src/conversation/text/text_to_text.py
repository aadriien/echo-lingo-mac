###############################################################################
##  `text_to_text.py`                                                        ##
##                                                                           ##
##  Purpose: LLM responses via local Mistral (Ollama)                       ##
###############################################################################


import ollama
from conversation.config import OLLAMA_MODEL


SYSTEM_PROMPTS = {
    "English": (
        "You are a friendly conversational partner. Reply in clear, casual English. "
        "Keep your reply proportional to what the user said: a short message gets a short reply, not an essay. "
        "Sound like a real person having a natural back-and-forth, not a teacher giving a lesson. "
        "Never add translations, definitions, or parenthetical notes in any other language."
    ),
    "Spanish": (
        "Eres un compañero de conversación amigable. Responde siempre en español claro y casual. "
        "Adapta la longitud de tu respuesta a lo que dijo el usuario: un mensaje corto merece una respuesta corta, no un ensayo. "
        "Suena como una persona real en una conversación natural, no como un profesor dando una lección. "
        "Nunca añadas traducciones, definiciones ni notas entre paréntesis en ningún otro idioma."
    ),
    "French": (
        "Tu es un partenaire de conversation amical. Réponds toujours en français clair et naturel. "
        "Adapte la longueur de ta réponse à ce que l'utilisateur a dit: un message court mérite une réponse courte, pas un essai. "
        "Parle comme une vraie personne dans une conversation naturelle, pas comme un professeur qui fait un cours. "
        "N'ajoute jamais de traductions, de définitions ni de notes entre parenthèses dans une autre langue."
    ),
    "German": (
        "Du bist ein freundlicher Gesprächspartner. Antworte immer auf Deutsch, klar und locker. "
        "Passe die Länge deiner Antwort an das an, was der Nutzer gesagt hat: auf eine kurze Nachricht kommt eine kurze Antwort, kein Aufsatz. "
        "Klinge wie ein echter Mensch in einem natürlichen Gespräch, nicht wie ein Lehrer, der einen Vortrag hält. "
        "Füge niemals Übersetzungen, Definitionen oder Anmerkungen in Klammern in einer anderen Sprache hinzu."
    ),
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