import logging
import os

import numpy as np
from fastapi import APIRouter

from ..features import UserExperience
from ..utils import dump_priors, get_ts

router = APIRouter()
ts = get_ts()
router = APIRouter()


@router.post("/train")
def train(user_experience: UserExperience):
    user_experience_dict = user_experience.dict()
    learner_id = user_experience_dict.get("learner_id")
    context = np.array(user_experience_dict.values())
    ts.sample(context, learner_id)
    to_dump_priors = os.environ["TO_DUMP_PRIORS"]
    if to_dump_priors == "yes":
        dump_priors(ts.prior_params)
    response = {"STATUS_CODE": 200}
    logging.info(f"returning response:{response}")
    return response
