import json
import os
from datetime import datetime

import boto3

from lingo_fit.model.thompson import ThompsonSampling


def reward_function(context, arm_action):
    """
    EXPLAIN: this is a placeholder for custom reward function
    :param context:
    :param arm_action:
    :return:
    """
    return arm_action


def get_ts() -> ThompsonSampling:
    if "ARMS_PRIOR_PATH" in os.environ:
        arms_priors_path = os.environ["ARMS_PRIOR_PATH"]
        arms_priors = load_arms_priors(arms_priors_path)
        return ThompsonSampling(
            reward_function=reward_function, arms_priors=arms_priors
        )

    return ThompsonSampling(reward_function=reward_function, arms_priors=None)


def parse_s3_path(s3_path: str) -> (str, str):
    s3_path = s3_path[5:]  # Remove the "s3://" prefix
    parts = s3_path.split("/", 1)
    bucket_name = parts[0]
    object_key = parts[1]
    return bucket_name, object_key


def load_arms_priors(arms_priors_path: str) -> dict:
    if arms_priors_path.startswith("s3://"):
        # Load from S3
        bucket_name, prefix = parse_s3_path(arms_priors_path)
        s3_client = boto3.client("s3")

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = response.get("Contents", [])

        if not objects:
            raise ValueError(
                f"No objects found in S3 path: {arms_priors_path}"
            )

        latest_object = max(objects, key=lambda obj: obj["LastModified"])
        latest_object_key = latest_object["Key"]

        response = s3_client.get_object(
            Bucket=bucket_name, Key=latest_object_key
        )
        arms_priors_json = response["Body"].read().decode("utf-8")
        arms_priors = json.loads(arms_priors_json)
    else:
        # Load from local file
        with open(arms_priors_path) as file:
            arms_priors = json.load(file)

    return arms_priors


def generate_timestamp_path(region: str, object_name: str) -> str:
    timestamp = f"{datetime.now()}"
    timestamped_path = (
        f"{object_name}/"
        f"region={region}/"
        f"timestamp={timestamp}/"
        f"{object_name}.json"
    )
    return timestamped_path


def dump_priors(prior_params: dict):
    """
    compute regret here
    :return:
    """

    bucket_name = os.environ["BUCKET"]
    region = os.environ["REGION"]

    # Serialize prior_params to JSON
    prior_params_json = json.dumps(prior_params)

    # Create an S3 client
    s3_client = boto3.client("s3", region_name=region)

    # Define the S3 object key
    s3_object_key = generate_timestamp_path(
        region=region, object_name="priors"
    )

    # Upload the JSON data to S3 bucket
    s3_client.put_object(
        Body=prior_params_json, Bucket=bucket_name, Key=s3_object_key
    )
