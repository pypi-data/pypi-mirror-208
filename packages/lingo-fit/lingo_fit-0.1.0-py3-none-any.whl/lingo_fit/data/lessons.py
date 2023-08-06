from typing import Dict, List

import numpy as np
from faker import Faker

from .languages import LANGUAGE_CODES


def generate_lessons_dataset(n_samples: int) -> List[Dict[str, str]]:
    """
    Generates a list of lesson models with fake data.

    Args:
        n_samples (int): The number of lesson models to generate.

    Returns:
        list: A list of dictionaries representing the lesson models.
    """
    fake = Faker()

    lesson_ids = np.random.randint(1, 60000, size=n_samples)
    names = [fake.sentence(nb_words=4) for _ in range(n_samples)]

    lessons_data = [
        {
            "lesson_id": str(lesson_ids[i]),
            "lesson_name": names[i],
            "language_id": language_id,
        }
        for language_id in LANGUAGE_CODES
        for i in range(n_samples)
    ]

    return lessons_data
