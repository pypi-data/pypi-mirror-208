import logging

import numpy as np
from fastapi import APIRouter

from ..utils import get_ts

ts = get_ts()
router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.post("/predict")
def predict(learner_id: str):
    logging.info("IN THE PREDICT ENDPOINT")
    # here we read context from SnowFlake database
    fixed_context_vector = np.array([[1, 2]])

    exercise_type = ts.predict(fixed_context_vector, learner_id)
    response = {"exercise_type": exercise_type}
    logging.info(f"returning response:{response}")
    return response
