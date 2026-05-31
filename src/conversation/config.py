###############################################################################
##  `config.py`                                                              ##
##                                                                           ##
##  Purpose: Central config / shared constants                               ##
###############################################################################


# Language options: Whisper language code + macOS neural voice for `say`
LANGUAGE_OPTIONS = {
    "English": {"code": "en-US", "voice": "Eddy (English (US))"},
    "Spanish": {"code": "es-ES", "voice": "Marisol (Enhanced)"},
    "French":  {"code": "fr-FR", "voice": "Audrey (Enhanced)"},
    "German":  {"code": "de-DE", "voice": "Anna (Enhanced)"},
}

DEFAULT_LANGUAGE = "Spanish"

# Ollama model
OLLAMA_MODEL = "mistral"
