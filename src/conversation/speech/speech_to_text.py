###############################################################################
##  `speech_to_text.py`                                                      ##
##                                                                           ##
##  Purpose: STT via sounddevice (capture) + mlx-whisper (on-device, Metal)  ##
###############################################################################


import numpy as np
import sounddevice as sd
import mlx_whisper

from conversation.config import LANGUAGE_OPTIONS

# mlx-community/whisper-small-mlx is a good default; swap in
# mlx-community/whisper-large-v3-turbo for better accuracy at modest latency cost.
_MODEL = "mlx-community/whisper-small-mlx"


class MacSTT:
    SAMPLE_RATE = 16_000

    def __init__(self, language="Spanish"):
        # "es-ES" → "es" — Whisper uses ISO 639-1 language codes
        self._lang = LANGUAGE_OPTIONS[language]["code"].split("-")[0]
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self):
        self._chunks = []
        self._stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, _frames, _time, _status):
        self._chunks.append(indata.copy())

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def get_transcript(self) -> str | None:
        if not self._chunks:
            return None
        audio = np.concatenate(self._chunks).flatten()
        result = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=_MODEL,
            language=self._lang,
        )
        return result["text"].strip() or None
