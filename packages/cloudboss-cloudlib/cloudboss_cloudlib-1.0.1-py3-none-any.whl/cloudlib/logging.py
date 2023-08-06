import logging

filtered_secrets = set()


class SecretAwareFormatter(logging.Formatter):
    def __init__(self, original_formatter):
        self.original_formatter = original_formatter
        super().__init__()

    def format(self, *args, **kwargs):
        message = self.original_formatter.format(*args, **kwargs)
        for pattern in filtered_secrets:
            message = message.replace(pattern, "*** SECRET ***")
        return message


def update_log_filter_with_secrets(secrets):
    filtered_secrets.update(secrets)
    filtered_secrets.update({secret.encode("unicode_escape").decode("utf8") for secret in secrets})
