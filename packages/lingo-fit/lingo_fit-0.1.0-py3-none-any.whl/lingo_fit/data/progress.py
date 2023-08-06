from typing import Dict, List

from faker import Faker


def generate_learning_progress_dataset(n_samples: int) -> List[Dict[str, str]]:
    """
    Generates a list of learning progress models with fake data.

    Args:
        n_samples (int): The number of learning progress models to generate.

    Returns:
        list: A list of dictionaries representing the learning progress models.
    """
    fake = Faker()

    learning_progress_data = [
        {
            "progress_id": fake.uuid4(),
            "learner_id": fake.uuid4(),
            "lesson_id": fake.uuid4(),
            "exercise_id": fake.uuid4(),
            "date_started": fake.date(),
            "date_completed": fake.date(),
            "time_spent": fake.time(),
            "score": fake.random_int(0, 100),
        }
        for _ in range(n_samples)
    ]

    return learning_progress_data
