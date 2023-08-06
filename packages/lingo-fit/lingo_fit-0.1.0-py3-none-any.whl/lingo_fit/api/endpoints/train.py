import logging
from typing import List

import numpy as np
from fastapi import APIRouter

from ..features import UserExperience
from ..utils import dump_priors, get_ts

router = APIRouter()
ts = get_ts()
router = APIRouter()


@router.post("/train")
def train(user_experience: List[UserExperience]):
    context = np.array(user_experience.dict().values())
    ts.sample(context)
    dump_priors(ts.prior_params)
    response = {"STATUS_CODE": 200}
    logging.info(f"returning response:{response}")
    return response
