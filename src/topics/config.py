TOPICS = [
    {
        "emoji": "💬",
        "names": {
            "English": "Freeform",
            "Spanish": "Libre",
            "French":  "Libre",
            "German":  "Frei",
        },
        "hints": None,
    },
    {
        "emoji": "🍕",
        "names": {
            "English": "Food",
            "Spanish": "Comida",
            "French":  "Cuisine",
            "German":  "Essen",
        },
        "hints": {
            "English": "food, cooking, recipes, restaurants, and local cuisine",
            "Spanish": "comida, cocina, recetas, restaurantes y gastronomía local",
            "French":  "nourriture, cuisine, recettes, restaurants et gastronomie locale",
            "German":  "Essen, Kochen, Rezepte, Restaurants und lokale Küche",
        },
    },
    {
        "emoji": "📚",
        "names": {
            "English": "Books",
            "Spanish": "Libros",
            "French":  "Livres",
            "German":  "Bücher",
        },
        "hints": {
            "English": "books, reading, authors, literary genres, and recommendations",
            "Spanish": "libros, lectura, autores, géneros literarios y recomendaciones",
            "French":  "livres, lecture, auteurs, genres littéraires et recommandations",
            "German":  "Bücher, Lesen, Autoren, Literaturgenres und Empfehlungen",
        },
    },
    {
        "emoji": "🎬",
        "names": {
            "English": "Movies & TV",
            "Spanish": "Cine y TV",
            "French":  "Cinéma & TV",
            "German":  "Filme & TV",
        },
        "hints": {
            "English": "movies, TV shows, actors, directors, and streaming favorites",
            "Spanish": "películas, series de TV, actores, directores y favoritos en streaming",
            "French":  "films, séries TV, acteurs, réalisateurs et favoris en streaming",
            "German":  "Filme, TV-Serien, Schauspieler, Regisseure und Streaming-Favoriten",
        },
    },
    {
        "emoji": "✈️",
        "names": {
            "English": "Travel",
            "Spanish": "Viajes",
            "French":  "Voyages",
            "German":  "Reisen",
        },
        "hints": {
            "English": "travel, destinations, cultures, and adventures abroad",
            "Spanish": "viajes, destinos, culturas y aventuras en el extranjero",
            "French":  "voyages, destinations, cultures et aventures à l'étranger",
            "German":  "Reisen, Reiseziele, Kulturen und Abenteuer im Ausland",
        },
    },
    {
        "emoji": "🐾",
        "names": {
            "English": "Animals",
            "Spanish": "Animales",
            "French":  "Animaux",
            "German":  "Tiere",
        },
        "hints": {
            "English": "animals, pets, wildlife, and nature",
            "Spanish": "animales, mascotas, vida silvestre y naturaleza",
            "French":  "animaux, animaux de compagnie, faune et nature",
            "German":  "Tiere, Haustiere, Wildtiere und Natur",
        },
    },
    {
        "emoji": "🎵",
        "names": {
            "English": "Music",
            "Spanish": "Música",
            "French":  "Musique",
            "German":  "Musik",
        },
        "hints": {
            "English": "music, songs, artists, concerts, and playlists",
            "Spanish": "música, canciones, artistas, conciertos y listas de reproducción",
            "French":  "musique, chansons, artistes, concerts et playlists",
            "German":  "Musik, Songs, Künstler, Konzerte und Playlists",
        },
    },
    {
        "emoji": "⚽",
        "names": {
            "English": "Sports",
            "Spanish": "Deportes",
            "French":  "Sports",
            "German":  "Sport",
        },
        "hints": {
            "English": "sports, teams, games, and athletes",
            "Spanish": "deportes, equipos, partidos y atletas",
            "French":  "sports, équipes, matchs et athlètes",
            "German":  "Sport, Mannschaften, Spiele und Athleten",
        },
    },
]


def topic_name(topic: dict, language: str) -> str:
    return topic["names"].get(language, topic["names"]["English"])


def topic_hint(topic: dict, language: str) -> str | None:
    if not topic.get("hints"):
        return None
    return topic["hints"].get(language, topic["hints"]["English"])
