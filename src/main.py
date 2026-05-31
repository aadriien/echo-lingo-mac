###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Entry point — wires STT > LLM > TTS pipeline                   ##
###############################################################################


from conversation.text.text_to_text import get_chat_response
from conversation.config import DEFAULT_LANGUAGE


def main():
    language = DEFAULT_LANGUAGE

    messages = [{"role": "user", "content": "Hola, ¿cómo estás hoy?"}]
    response = get_chat_response(messages, language=language)
    print(f"Mistral: {response}")


if __name__ == "__main__":
    main()
