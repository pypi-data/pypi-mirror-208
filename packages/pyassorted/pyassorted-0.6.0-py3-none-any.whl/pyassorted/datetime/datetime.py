import datetime
import pytz
from typing import Text, Union


def aware_datetime_now(
    tz: Union[Text, "pytz.BaseTzInfo"] = pytz.UTC
) -> "datetime.datetime":
    """Get the current datetime in the specified timezone.

    Parameters
    ----------
    tz : Union[Text, pytz.BaseTzInfo], optional
        The timezone, by default pytz.UTC

    Returns
    -------
    datetime.datetime
        The current datetime in the specified timezone.
    """

    tz = pytz.timezone(tz) if isinstance(tz, Text) else tz
    utc_dt = pytz.UTC.localize(datetime.datetime.utcnow())
    return utc_dt.astimezone(tz)


def iso_datetime_now(tz: Union[Text, "pytz.BaseTzInfo"] = pytz.UTC) -> Text:
    """Get the current datetime in the specified timezone as an ISO 8601 string.

    Parameters
    ----------
    tz : Union[Text, pytz.BaseTzInfo], optional
        The timezone, by default pytz.UTC

    Returns
    -------
    Text
        The current datetime in the specified timezone as an ISO 8601 string.
    """

    return aware_datetime_now(tz).isoformat()
