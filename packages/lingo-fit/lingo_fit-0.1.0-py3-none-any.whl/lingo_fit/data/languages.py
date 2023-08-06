import random
from typing import Dict, List

LANGUAGE_CODES = {
    "es": "Spanish",
    "no": "Norwegian",
    "pl": "Polish",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "nl": "Dutch",
    "tr": "Turkish",
    "id": "Indonesian",
    "da": "Danish",
    "sv": "Swedish",
    "en": "English",
}


def generate_languages_dataset(n_samples) -> List[Dict]:
    return [
        {"language_id": random.choice(list(LANGUAGE_CODES.keys()))}
        for _ in range(n_samples)
    ]
