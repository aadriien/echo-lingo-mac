###############################################################################
##  `config.py`                                                              ##
##                                                                           ##
##  Purpose: Central config / shared constants                               ##
###############################################################################


# Language options: Whisper language code + macOS neural voice for `say`
LANGUAGE_OPTIONS = {
    "English": {"code": "en-US", "voice": "Eddy (English (US))"},
    "Spanish": {"code": "es-ES", "voice": "Eddy (Spanish (Spain))"},
    "French":  {"code": "fr-FR", "voice": "Eddy (French (France))"},
    "German":  {"code": "de-DE", "voice": "Eddy (German (Germany))"},
}

DEFAULT_LANGUAGE = "Spanish"

# Ollama model
OLLAMA_MODEL = "mistral"
