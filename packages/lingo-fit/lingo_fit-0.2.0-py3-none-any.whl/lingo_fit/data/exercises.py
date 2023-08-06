from typing import Any, Dict, List

import numpy as np
from faker import Faker
from scipy import stats

from .languages import LANGUAGE_CODES

EXERCISE_TYPES = ("Listening", "Writing", "Speaking", "FlashCards")


def generate_exercises_dataset(n_samples: int) -> List[Dict[str, str]]:
    """
    Generates a list of exercise models with fake data.

    Args:
        n_samples (int): The number of exercise models to generate.

    Returns:
        list: A list of dictionaries representing the exercise models.
    """
    fake = Faker()
    LANGUAGE_CODES

    exercise_data = [
        {
            "exercise_id": fake.uuid4(),
            "exercise_name": fake.word(),
            "exercise_type": exercise_type,
            "language_id": language_id,
            "level": fake.random_int(1, 10),
            "time_to_complete": fake.random_int(5, 60),
        }
        for language_id in LANGUAGE_CODES
        for exercise_type in EXERCISE_TYPES
        for _ in range(n_samples)
    ]

    return exercise_data


def generate_exercises_success_status(beta_params: Dict[str, Any]):
    # Define the Beta-Bernoulli model parameters for each exercise type

    # Generate a completion status for
    # each exercise type using the Beta-Bernoulli distribution
    completion_probabilities = []
    for exercise_type in EXERCISE_TYPES:
        completion_prob = np.random.beta(*beta_params[exercise_type])
        has_completed = stats.bernoulli.rvs(completion_prob)
        completion_probabilities.append(
            {"has_completed": has_completed, "exercise_type": exercise_type}
        )
    return completion_probabilities
