"""
General utility functions for the application.
"""

import datetime
import secrets
import string

from ecombot.config import settings


def generate_order_number() -> str:
    """
    Generates a unique order number.
    Format: JJJ-HHMMSS-XXXX
    - JJJ: Julian Date (Day of year, 001-366)
    - HHMMSS: Time (Hours, Minutes, Seconds)
    - XXXX: 4 random alphanumeric characters
    """
    now = datetime.datetime.now(settings.get_zoneinfo())
    date_part = now.strftime("%j")
    time_part = now.strftime("%H%M%S")

    chars = string.ascii_lowercase + string.digits
    random_part = "".join(secrets.choice(chars) for _ in range(4))

    return f"{date_part}-{time_part}-{random_part}"
