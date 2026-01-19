"""
General utility functions for the application.
"""

import asyncio
import datetime
from pathlib import Path
import secrets
import string

from PIL import Image

from ecombot.config import settings
from ecombot.logging_setup import log


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


def compress_image_sync(
    file_path: str, quality: int = 85, max_size: tuple[int, int] = (1280, 1280)
) -> None:
    """
    Compresses and resizes an image in place using Pillow.
    Converts PNG/RGBA to JPEG/RGB to save space.
    """
    try:
        path = Path(file_path)
        with Image.open(path) as img:
            # Convert to RGB if necessary (e.g. for PNGs with transparency)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize if larger than max_size, maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save back to the same path, optimized
            img.save(path, "JPEG", quality=quality, optimize=True)

        log.info(f"Compressed image: {file_path}")
    except Exception as e:
        log.error(f"Failed to compress image {file_path}: {e}")


async def compress_image(file_path: str) -> None:
    """Async wrapper to run compression in a separate thread."""
    await asyncio.to_thread(compress_image_sync, file_path)
