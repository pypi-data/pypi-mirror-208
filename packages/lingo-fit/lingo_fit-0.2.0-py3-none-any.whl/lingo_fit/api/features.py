"""
The InferenceFeatures class is a Pydantic BaseModel
that represents the features used for venue rating inference.
"""
from pydantic import BaseModel, Field


class UserExperience(BaseModel):
    learner_id: str = Field(
        "4202398962129790175",
        description="ID of the venue being recommended",
        example="4202398962129790175",
    )
    lesson_id: str = Field(
        "spanish_sangria",
        description="unique name of lesson",
        example="spanish_sangria",
    )
    exercise_id: str = Field(
        "funny_words",
        description="unique name of exercise",
        example="funny_words",
    )
    time_spent: int = Field(
        8,
        description="time in minutes spent solving",
        ge=1,
        le=60,
    )
    exercise_level: int = Field(
        2,
        description="how difficult exercise is",
        example=2,
    )

    has_completed: bool = Field(
        True,
        description="has user solved exercise",
        example=True,
    )
