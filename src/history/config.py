SUMMARIZE_PROMPTS = {
    "English": (
        "Read this conversation and output 3-5 short phrases (no full sentences) "
        "capturing only specific things mentioned: names, titles, places, opinions, preferences. "
        "One phrase per line. No preamble, no labels, nothing generic."
    ),
    "Spanish": (
        "Lee esta conversación y escribe 3-5 frases cortas (sin oraciones completas) "
        "sobre cosas específicas mencionadas: nombres, títulos, lugares, opiniones, preferencias. "
        "Una frase por línea. Sin preámbulo, sin etiquetas, nada genérico."
    ),
    "French": (
        "Lis cette conversation et écris 3 à 5 courtes phrases (sans phrases complètes) "
        "sur des choses spécifiques mentionnées : noms, titres, lieux, opinions, préférences. "
        "Une phrase par ligne. Pas de préambule, pas d'étiquettes, rien de générique."
    ),
    "German": (
        "Lies dieses Gespräch und schreibe 3-5 kurze Phrasen (keine vollständigen Sätze) "
        "über spezifisch erwähnte Dinge: Namen, Titel, Orte, Meinungen, Vorlieben. "
        "Eine Phrase pro Zeile. Keine Einleitung, keine Labels, nichts Allgemeines."
    ),
}

# Injected into the system prompt when saved history exists for the active topic.
# {bullets} is substituted with a semicolon-joined list of past bullet points.
HISTORY_CONTEXT = {
    "English": "Previously discussed about this topic: {bullets}.",
    "Spanish": "Temas tratados anteriormente sobre este tema: {bullets}.",
    "French":  "Sujets précédemment abordés sur ce thème : {bullets}.",
    "German":  "Zuvor zu diesem Thema Besprochenes: {bullets}.",
}
