###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Entry point — wires STT > LLM > TTS pipeline                   ##
###############################################################################


import time

from conversation.config import DEFAULT_LANGUAGE
from conversation.speech.speech_to_text import WhisperSTT
from conversation.speech.text_to_speech import speak
from conversation.text.text_to_text import get_chat_response


def main():
    language = DEFAULT_LANGUAGE
    stt = WhisperSTT(language=language)
    history = []

    print(f"Language: {language}")
    print("Press Enter to start speaking. Empty input to quit.\n")

    while True:
        raw = input("[ Press Enter to speak ] ")
        if raw.strip().lower() in ("q", "quit", "exit"):
            break

        stt.start()
        input("[ Recording — press Enter to stop ] ")
        stt.stop()

        user_text = stt.get_transcript()
        if not user_text:
            print("(nothing heard, try again)\n")
            continue

        print(f"You: {user_text}")

        history.append({"role": "user", "content": user_text})
        reply = get_chat_response(history, language=language)
        history.append({"role": "assistant", "content": reply})

        print(f"Assistant: {reply}\n")
        speak(reply, language=language)

        time.sleep(0.75)


if __name__ == "__main__":
    main()
