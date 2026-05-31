###############################################################################
##  `config.py`                                                              ##
##                                                                           ##
##  Purpose: Central config / shared constants                               ##
###############################################################################


# Language options: code for SFSpeechRecognizer, voice name for `say`
LANGUAGE_OPTIONS = {
    "English": {"code": "en-US", "voice": "Samantha"},
    "Spanish": {"code": "es-ES", "voice": "Monica"},
    "French":  {"code": "fr-FR", "voice": "Thomas"},
    "German":  {"code": "de-DE", "voice": "Anna"},
}

DEFAULT_LANGUAGE = "Spanish"

# Ollama model
OLLAMA_MODEL = "mistral"
