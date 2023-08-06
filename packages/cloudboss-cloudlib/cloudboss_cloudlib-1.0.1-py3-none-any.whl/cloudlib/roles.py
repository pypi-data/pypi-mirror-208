import boto3

sts = boto3.client("sts")


def assume_role(role_arn):
    response = sts.assume_role(RoleArn=role_arn, RoleSessionName="cloudboss-cloudlib-session")

    new_session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    return new_session
