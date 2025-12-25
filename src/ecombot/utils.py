"""
General utility functions for the application.
"""

import datetime
import random
import string


def generate_order_number() -> str:
    """
    Generates a unique, human-readable order number.
    Format: ECO-YYMMDD-XXXX
    - ECO: Prefix for our EcomBot store
    - YYMMDD: Current date
    - XXXX: 4 random alphanumeric characters (excluding ambiguous ones)
    """
    try:
        date_part = datetime.datetime.now(datetime.UTC).strftime("%y%m%d")

        chars = string.ascii_uppercase.replace("O", "").replace(
            "I", ""
        ) + string.digits.replace("0", "").replace("1", "")
        random_part = "".join(random.choices(chars, k=4))

        return f"ECO-{date_part}-{random_part}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate order number: {e}") from e
