###############################################################################
##  `app_controller.py`                                                      ##
##                                                                           ##
##  Purpose: Conversation pipeline: STT → TTT → TTS, zero UI imports         ##
###############################################################################


import threading
import time

from conversation.config import DEFAULT_LANGUAGE
from conversation.speech.speech_to_text import WhisperSTT
from conversation.speech.text_to_speech import speak
from conversation.text.text_to_text import get_chat_response


class ConversationController:
    """
    Owns all language/conversation state and drives the STT → TTT → TTS
    pipeline on a background thread. Communicates entirely through the five
    callbacks supplied at construction. No AppKit or display code here.

    Callbacks are invoked from whatever thread is convenient (main thread for
    synchronous ones, background thread inside _run_pipeline). The GUI layer
    is responsible for marshalling them to the main thread if needed.
    """

    def __init__(self, *, on_status, on_user_bubble, on_assistant_bubble,
                 on_mic_reset, on_mic_disabled):
        self._on_status           = on_status
        self._on_user_bubble      = on_user_bubble
        self._on_assistant_bubble = on_assistant_bubble
        self._on_mic_reset        = on_mic_reset
        self._on_mic_disabled     = on_mic_disabled

        self._language  = DEFAULT_LANGUAGE
        self._history   = []
        self._stt       = WhisperSTT(language=self._language)
        self._recording = False

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def language(self) -> str:
        return self._language

    @property
    def recording(self) -> bool:
        return self._recording

    # ── public interface ──────────────────────────────────────────────────────

    def set_language(self, lang: str):
        self._language = lang
        self._stt      = WhisperSTT(language=lang)
        self._history  = []

    def start_recording(self):
        self._recording = True
        self._stt.start()

    def stop_recording(self):
        self._recording = False
        self._stt.stop()
        self._on_mic_disabled()
        self._on_status("Transcribing…")
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    # ── pipeline ──────────────────────────────────────────────────────────────

    def _run_pipeline(self):
        text = self._stt.get_transcript()
        if not text:
            self._on_status("Nothing heard. Tap to try again")
            self._on_mic_reset()
            return

        self._on_user_bubble(text)
        self._history.append({"role": "user", "content": text})

        self._on_status("Thinking…")
        try:
            reply = get_chat_response(self._history, language=self._language)
        except RuntimeError as e:
            self._on_status(str(e))
            self._on_mic_reset()
            return

        self._history.append({"role": "assistant", "content": reply})
        self._on_assistant_bubble(reply)

        self._on_status("Speaking…")
        speak(reply, language=self._language)

        time.sleep(0.75)
        self._on_status("Tap to speak")
        self._on_mic_reset()