SUMMARIZE_PROMPTS = {
    "English": 'List 1-3 key noun phrases from the text. Max 4 words each. One per line. Example output:\nwhale sharks\nHarry Potter\nNo sentences. No verbs. No filler.',
    "Spanish": 'Lista 1-3 frases nominales clave del texto. Máximo 4 palabras cada una. Una por línea. Ejemplo:\ntiburones ballena\nHarry Potter\nSin oraciones. Sin verbos.',
    "French":  'Liste 1-3 phrases nominales clés du texte. 4 mots max chacune. Une par ligne. Exemple :\nrequins baleine\nHarry Potter\nPas de phrases. Pas de verbes.',
    "German":  'Liste 1-3 Schlüssel-Nominalphrasen aus dem Text. Max. 4 Wörter pro Phrase. Eine pro Zeile. Beispiel:\nWalhaie\nHarry Potter\nKeine Sätze. Keine Verben.',
}

REDUCE_PROMPTS = {
    "English": "Pick the 2-4 most important. Max 4 words each. One per line. No sentences.",
    "Spanish": "Elige las 2-4 más importantes. Máximo 4 palabras cada una. Una por línea. Sin oraciones.",
    "French":  "Garde les 2-4 plus importantes. 4 mots max chacune. Une par ligne. Pas de phrases.",
    "German":  "Wähle die 2-4 wichtigsten. Max. 4 Wörter pro Zeile. Eine pro Zeile. Keine Sätze.",
}

# Injected into the system prompt when saved history exists for the active topic.
# {bullets} is substituted with a semicolon-joined list of past bullet points.
HISTORY_CONTEXT = {
    "English": "Previously discussed about this topic: {bullets}.",
    "Spanish": "Temas tratados anteriormente sobre este tema: {bullets}.",
    "French":  "Sujets précédemment abordés sur ce thème : {bullets}.",
    "German":  "Zuvor zu diesem Thema Besprochenes: {bullets}.",
}
