from typing import Dict, List

from faker import Faker


def generate_subscriptions_dataset(n_samples: int) -> List[Dict[str, str]]:
    """
    Generates a list of subscription models with fake data.

    Args:
        n_samples (int): The number of subscription models to generate.

    Returns:
        list: A list of dictionaries representing the subscription models.
    """
    fake = Faker()

    subscription_data = [
        {
            "subscription_id": fake.uuid4(),
            "name": fake.word(),
            "price": fake.random_int(50, 500),
        }
        for _ in range(n_samples)
    ]

    return subscription_data
