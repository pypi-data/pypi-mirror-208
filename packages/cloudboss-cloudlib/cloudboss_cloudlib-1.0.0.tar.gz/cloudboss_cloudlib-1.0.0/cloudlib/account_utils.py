import functools
import logging

import boto3
from botocore.exceptions import ClientError

from cloudlib.constants import LIST_ACCOUNT_ROLE
from cloudlib.exceptions import MissingResourceException
from cloudlib.roles import assume_role

logger = logging.getLogger(__name__)

config = Config(retries={"max_attempts": 30})

iam_client = boto3.client("iam")
organizations_client = boto3.client("organizations", config=config)
sts_client = boto3.client("sts")


@functools.lru_cache
def get_organization_id():
    return organizations_client.describe_organization()["Organization"]["Id"]


@functools.lru_cache
def get_current_account_alias():
    try:
        current_account_alias = iam_client.list_account_aliases()["AccountAliases"][0]
    except IndexError as exc:
        raise MissingResourceException("Could not get current account alias") from exc

    logger.info("Current account alias: %s", current_account_alias)
    return current_account_alias


@functools.lru_cache
def get_current_account_id():
    return sts_client.get_caller_identity()["Account"]


@functools.lru_cache
def get_master_account_id():
    return organizations_client.describe_organization()["Organization"]["MasterAccountId"]


@functools.lru_cache
def get_account_id(account_name):
    for account in _list_accounts():
        if account_name == account["Name"]:
            return account["Id"]
    raise MissingResourceException(f"Could not find account id for name: {account_name}")


@functools.lru_cache
def _list_accounts():
    master_account_id = get_master_account_id()
    list_accounts_role_arn = f"arn:aws:iam::{master_account_id}:role/{LIST_ACCOUNT_ROLE}"
    try:
        org_client = assume_role(list_accounts_role_arn).client("organizations", config=config)
    except ClientError as exc:
        # If we get an AccessDenied, we are probably not in the master account
        if "AccessDenied" in str(exc):
            if master_account_id == get_current_account_id():
                logger.warning(
                    "Could not assume role to list accounts, using current credentials assuming "
                    "this is the bootstrap process."
                )
                org_client = boto3.client("organizations", config=config)
            else:
                raise MissingResourceException(
                    "Could not assume role, and not in master account"
                ) from exc
        else:
            raise

    return org_client.get_paginator("list_accounts").paginate().build_full_result()["Accounts"]
