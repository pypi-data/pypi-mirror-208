import random
import uuid

from faker import Faker


def generate_learners_dataset(n_learners):
    fake = Faker()
    learners = []
    for i in range(n_learners):
        # Generate fake data for each field
        learner_id = uuid.uuid4()
        name = fake.name()
        email = fake.email()
        password = fake.password()
        subscription_id = random.randint(1, 5)
        language_id = random.randint(1, 10)
        goal_id = random.randint(1, 20)

        # Add the generated data to the list of learners
        learners.append(
            {
                "learner_id": str(learner_id),
                "name": name,
                "email": email,
                "password": password,
                "subscription_id": subscription_id,
                "language_id": language_id,
                "goal_id": goal_id,
            }
        )

    return learners
