###############################################################################
##  `text_to_text.py`                                                        ##
##                                                                           ##
##  Purpose: LLM responses via local Mistral (Ollama)                       ##
###############################################################################


import ollama
from conversation.config import OLLAMA_MODEL


SYSTEM_PROMPTS = {
    "English": "You are a friendly and natural conversational partner. Reply in clear, casual English.",
    "Spanish": "Eres un compañero de conversación amigable y natural. Responde en español claro y casual.",
    "French":  "Tu es un partenaire de conversation amical et naturel. Réponds en français clair et naturel.",
    "German":  "Du bist ein freundlicher und natürlicher Gesprächspartner. Antworte in klarem, lockerem Deutsch.",
}


def get_chat_response(messages, language="Spanish"):
    # messages: full conversation history as list of {"role": ..., "content": ...}
    system = {"role": "system", "content": SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["English"])}

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[system] + messages,
    )
    return response["message"]["content"]
