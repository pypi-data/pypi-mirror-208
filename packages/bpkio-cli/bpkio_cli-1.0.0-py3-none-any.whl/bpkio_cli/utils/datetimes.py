from datetime import datetime
from typing import Optional

import arrow
import dateparser
import pytz


def parse_date_string(date: str) -> float:
    return dateparser.parse(date).timestamp()


def get_utc_date_ranges(
    from_time: datetime, to_time: Optional[datetime] = None, unit: str = "month"
):
    if to_time:
        end = arrow.get(to_time)
    else:
        end = arrow.utcnow()

    start = arrow.get(from_time).replace(hour=0, minute=0, second=0, microsecond=0)

    range = arrow.Arrow.span_range(unit, start=start, end=end, exact=True)  # type: ignore

    return [(s.datetime, e.datetime) for (s, e) in range]


def parse_date_expression_as_utc(exp: str | tuple | list) -> datetime:
    if isinstance(exp, (tuple, list)):
        exp = " ".join(exp)

    current_tz_name = datetime.now().astimezone().strftime("%Z")
    # current_tz_name = current_tz.zone

    # Parse the input string into a datetime object considering the timezone information
    dt_local = dateparser.parse(
        exp, settings={"TIMEZONE": current_tz_name, "RETURN_AS_TIMEZONE_AWARE": True}
    )

    # Convert the datetime object to UTC timezone
    dt_utc = dt_local.astimezone(pytz.UTC)

    return dt_utc
