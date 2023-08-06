import datetime


def constellation_date_string(dt):
    """Return a datetime formatted in the format constellation wants as a string like: 2021-02-17T15:16:36Z

    Note - the datetime object must be in utc time."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def constellation_date_from_string(date_string):
    """Return a datetime object from the string format that constellation uses like: 2021-02-09T04:12:02.618767Z

    Note - the datetime object will be in utc time."""
    # Handle both second and subsecond precision on datetimes
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
