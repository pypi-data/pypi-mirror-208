import uuid
from typing import Dict, List

import polars as pl

from .exercises import (
    EXERCISE_TYPES,
    generate_exercises_dataset,
    generate_exercises_success_status,
)
from .languages import generate_languages_dataset
from .lessons import LANGUAGE_CODES, generate_lessons_dataset


def generate_experiences_dataset(
    n_users: int,
    n_exercises_per_user: int,
    number_of_daily_lessons_per_user: int,
    beta_params: dict,
) -> List[Dict[str, str]]:
    # Generate language preferences for each user
    language_preferences = generate_languages_dataset(n_samples=n_users)

    # Generate experience records for each language preference
    user_ids = [str(uuid.uuid4()) for _ in range(n_users)]
    user_ids_series = pl.Series(user_ids, dtype=pl.Utf8)
    language_ids = pl.Series(
        [lang_pref["language_id"] for lang_pref in language_preferences],
        dtype=pl.Utf8,
    )
    experience_records = pl.DataFrame(
        {"user_id": user_ids_series, "language_id": language_ids}
    )

    assert experience_records.shape[0] == n_users
    # Generate language and lesson records for each experience record
    n_exercises = n_users * n_exercises_per_user
    exercises_records = pl.DataFrame(
        generate_exercises_dataset(n_samples=n_exercises)
    )
    n_exercise_types = len(EXERCISE_TYPES)
    n_languages = len(LANGUAGE_CODES)
    assert (
        exercises_records.shape[0]
        == n_exercises * n_exercise_types * n_languages
    )

    n_lessons = n_users * number_of_daily_lessons_per_user
    lessons_records = pl.DataFrame(
        generate_lessons_dataset(n_samples=n_lessons)
    )
    assert lessons_records.shape[0] == n_lessons * n_languages

    # Join language and lesson records to experience records
    n_rows = experience_records.shape[0]
    experience_records = experience_records.join(
        exercises_records, on="language_id", how="left"
    )
    assert (
        experience_records.shape[0] == n_rows * n_exercises * n_exercise_types
    )
    n_rows = experience_records.shape[0]
    experience_records = experience_records.join(
        lessons_records, on="language_id", how="left"
    )
    assert experience_records.shape[0] == n_lessons * n_rows

    # Generate completion probabilities for each exercise type

    completion_probabilities = pl.DataFrame(
        generate_exercises_success_status(beta_params)
    )

    # Join completion probabilities to experience records
    experience_records = experience_records.join(
        completion_probabilities, on="exercise_type", how="left"
    )

    return experience_records
