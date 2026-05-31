###############################################################################
##  `text_to_speech.py`                                                      ##
##                                                                           ##
##  Purpose: TTS using macOS `say` command                                  ##
###############################################################################


import subprocess
from conversation.config import LANGUAGE_OPTIONS


def speak(text, language="Spanish"):
    voice = LANGUAGE_OPTIONS[language]["voice"]
    # Blocks until audio playback finishes — intentional, keeps pipeline sequential
    subprocess.run(["say", "-v", voice, text], check=True)
