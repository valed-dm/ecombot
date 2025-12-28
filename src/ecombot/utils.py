"""
General utility functions for the application.
"""

import datetime
import secrets
import string


def generate_order_number() -> str:
    """
    Generates a unique, human-readable order number.
    Format: ECO-YYMMDD-XXXX
    - ECO: Prefix for our EcomBot store
    - YYMMDD: Current date
    - XXXX: 4 random alphanumeric characters (excluding ambiguous ones)
    """
    date_part = datetime.datetime.now(datetime.UTC).strftime("%y%m%d")

    chars = string.ascii_uppercase.replace("O", "").replace(
        "I", ""
    ) + string.digits.replace("0", "").replace("1", "")
    random_part = "".join(secrets.choice(chars) for _ in range(4))

    return f"ECO-{date_part}-{random_part}"
