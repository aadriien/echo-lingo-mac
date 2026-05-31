###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Entry point — wires STT > LLM > TTS pipeline                   ##
###############################################################################


from conversation.speech.speech_to_text import MacSTT
from conversation.text.text_to_text import get_chat_response
from conversation.speech.text_to_speech import speak
from conversation.config import DEFAULT_LANGUAGE


def main():
    stt = MacSTT(language=DEFAULT_LANGUAGE)
    stt.start()

    conversation_history = []

    # TODO: main conversation loop
    #   - stt.get_transcript() → user text
    #   - append user turn to conversation_history
    #   - get_chat_response(conversation_history, language) → reply
    #   - append assistant turn to conversation_history
    #   - speak(reply, language)


if __name__ == "__main__":
    main()
