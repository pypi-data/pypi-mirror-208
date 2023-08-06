import logging
from typing import Callable, Tuple

import numpy as np

from ..data import EXERCISE_TYPES


def validate_priors(arms_priors: Tuple[float, float]):
    expected_number_of_priors = len(EXERCISE_TYPES)
    actual_number_of_priors = len(arms_priors)
    return actual_number_of_priors != expected_number_of_priors


class ThompsonSampling:
    def __init__(
        self,
        reward_function: Callable,
        arms_priors: Tuple[float, float],
    ):
        is_valid_prior = validate_priors(arms_priors) if arms_priors else False
        self.prior_params = (
            arms_priors
            if is_valid_prior
            else {
                exercise_type: (
                    np.random.uniform(0, 1),
                    np.random.uniform(0, 1),
                )
                for exercise_type in EXERCISE_TYPES
            }
        )

        info_message = """
        Insufficient number of prior parameters supplied.
        Therefore, priors were generated randomly
        """
        if not is_valid_prior:
            logging.info(info_message)

        self.n_arms = len(EXERCISE_TYPES)
        self.best_arm = None
        if not isinstance(reward_function, Callable):
            raise ValueError("reward_function is expected to be 'Callable'")
        self.reward_function = reward_function

    def sample(self, context: np.array, learner_id: str) -> int:
        """Samples an arm using the Thompson Sampling algorithm.

        Parameters:
            context (np.ndarray): The context for which to choose an arm.

        Returns:
            int: The index of the arm to pull.
        """

        expected_rewards, best_arm = self._compute_expected_rewards(
            context, learner_id
        )

        # Update counts, successes, and failures for chosen arm
        highest_expected_reward = expected_rewards[best_arm]
        self.update_prior(best_arm, highest_expected_reward)

        self.best_arm = best_arm

    def _compute_expected_rewards(
        self, context: np.ndarray, learner_id: str
    ) -> Tuple[np.ndarray, int]:
        """Computes the expected
        rewards for each arm and
        returns the best arm."""
        expected_rewards = dict.fromkeys(self.prior_params.keys())

        logging.info(f"calculating reward for learner {learner_id}")
        for arm, (alpha, beta) in self.prior_params.items():
            arm_action = np.random.beta(alpha, beta)
            current_reward_value = self.reward(context, arm_action)
            expected_rewards[arm] = current_reward_value

        best_arm = max(expected_rewards, key=expected_rewards.get)
        best_value = expected_rewards[best_arm]
        info_message = f"""
        the arm {best_arm} has the highest sampled value {best_value}
        """
        logging.info(info_message)
        return expected_rewards, best_arm

    def predict(self, context: np.array, learner_id: str) -> int:
        """Predicts the arm to pull
        for the given context using
        the current prior distribution parameters.

        Parameters:
            context (np.ndarray):
            learner_id (str): id of a person learning
            The context for which to choose an arm.

        Returns:
            int: The index of the arm to pull.
        """
        expected_rewards, best_arm = self._compute_expected_rewards(
            context, learner_id
        )
        info_message = f"""
            The reward for the given context: {context}
            and learner_id: {learner_id}
            is {expected_rewards}
        """
        logging.info(info_message)
        return best_arm

    def reward(self, context: np.array, arm_action: int) -> int:
        """Returns the reward for pulling the given arm given the context x."""
        # EXPLAIN: this is a placeholder
        # TODO: Implement reward function

        reward_value = self.reward_function(context, arm_action)
        info_message = f"""
            Returning reward value: {reward_value}
            for the given arm action: {arm_action}",
            in the context: {context}
        """
        logging.info(info_message)
        return reward_value

    def update_prior(self, arm: int, highest_reward: int):
        """Updates the prior distribution
        parameters for the given arm
        based on the observed reward."""

        prior_alpha, prior_beta = self.prior_params[arm]
        alpha = prior_alpha + highest_reward
        beta = prior_beta + (1 - highest_reward)
        info_message = f"""
        for the current best arm: {arm}
        updating its prior distribution params
        alpha:{prior_alpha}, beta: {prior_beta} according
        to the observed current reward {highest_reward}.
        The updated values are:
        new_alpha: {alpha}, new_beta: {beta}
        """
        logging.info(info_message)
        self.prior_params[arm] = (alpha, beta)

    def regrets(self):
        """
        compute regret here
        :return:
        """
