import datetime


def get_current_datetime():
    return datetime.datetime.now(datetime.timezone.utc)


def get_current_datetime_string():
    return get_current_datetime().isoformat()
