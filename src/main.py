###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Entry point — wires STT > LLM > TTS pipeline                   ##
###############################################################################


from conversation.config import DEFAULT_LANGUAGE
from conversation.speech.speech_to_text import WhisperSTT
from conversation.speech.text_to_speech import speak


def main():
    language = DEFAULT_LANGUAGE
    stt = WhisperSTT(language=language)

    print(f"Language: {language}")
    input("Press Enter to start recording...")
    stt.start()
    input("Recording — press Enter to stop...")
    stt.stop()

    print("Transcribing...")
    text = stt.get_transcript()
    print(f"Transcript: {text!r}")

    if text:
        print("Speaking...")
        speak(text, language=language)


if __name__ == "__main__":
    main()
