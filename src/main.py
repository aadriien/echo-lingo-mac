###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Entry point — wires STT > LLM > TTS pipeline                   ##
###############################################################################


from conversation.config import DEFAULT_LANGUAGE
from conversation.speech.speech_to_text import WhisperSTT


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


if __name__ == "__main__":
    main()
