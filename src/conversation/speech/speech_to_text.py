###############################################################################
##  `speech_to_text.py`                                                      ##
##                                                                           ##
##  Purpose: STT using macOS SFSpeechRecognizer via pyobjc                  ##
###############################################################################


# TODO: implement using pyobjc-framework-Speech + pyobjc-framework-AVFoundation
#
# Approach:
#   - SFSpeechRecognizer for recognition (supports en/es/fr/de on-device)
#   - AVAudioEngine for microphone capture
#   - SFSpeechAudioBufferRecognitionRequest for real-time audio buffer streaming
#   - Delegate callbacks → thread-safe queue so callers block on get_transcript()


class MacSTT:
    def __init__(self, language="Spanish"):
        # TODO: resolve language code from config.LANGUAGE_OPTIONS
        # TODO: initialize SFSpeechRecognizer with that locale
        # TODO: initialize AVAudioEngine + input node tap
        pass

    def start(self):
        # TODO: request speech recognition authorization
        # TODO: start AVAudioEngine
        # TODO: attach recognition request to engine input tap
        pass

    def stop(self):
        # TODO: stop engine, end recognition request, clean up
        pass

    def get_transcript(self, timeout=5):
        # TODO: block on internal queue until a finalized transcript arrives
        # Returns transcript string or None on timeout
        pass
