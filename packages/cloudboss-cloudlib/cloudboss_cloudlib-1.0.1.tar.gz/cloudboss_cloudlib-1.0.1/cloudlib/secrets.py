import functools
import json
import logging

import boto3

logger = logging.getLogger(__name__)
secrets_manager_client = boto3.client("secretsmanager")


def build_base_arn(region, account_id):
    return f"arn:aws:secretsmanager:{region}:{account_id}:secret:"


def get_secret(arn_base, id_with_key):
    logger.info("Fetching secret, base: %s id_with_key: %s", arn_base, id_with_key)
    secret_id, nested_key = id_with_key.split(":")
    response = _get_secret(arn_base, secret_id)
    logger.debug("After fetching secret %s %s", arn_base, id_with_key)
    secrets_for_id = json.loads(response["SecretString"])
    return secrets_for_id[nested_key]


@functools.lru_cache
def _get_secret(arn_base, secret_id):
    full_secret_id = arn_base + secret_id
    response = secrets_manager_client.get_secret_value(
        SecretId=full_secret_id, VersionStage="AWSCURRENT"
    )
    return response
