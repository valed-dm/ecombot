"""Common utilities for checkout process."""

from html import escape
from typing import Optional

from ecombot.core.manager import central_manager as manager
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.schemas.dto import CartDTO


def get_default_address(user: User) -> Optional[DeliveryAddress]:
    """Get user's default delivery address."""
    return next((addr for addr in user.addresses if addr.is_default), None)


def determine_missing_info(
    user: User, default_address: Optional[DeliveryAddress]
) -> list[str]:
    """Determine what information is missing for checkout."""
    missing_info = []
    if not user.phone:
        missing_info.append("phone number")
    if not default_address:
        missing_info.append("default address")
    return missing_info


def generate_fast_path_confirmation_text(
    user: User, default_address: DeliveryAddress, cart: CartDTO
) -> str:
    """Generate confirmation text for fast path checkout."""
    return (
        manager.get_message(
            "checkout",
            "fast_path_confirm",
            address=escape(default_address.full_address or ""),
            phone=escape(user.phone or "Not set"),
        )
        + f"\n\n<b>Total Price: ${cart.total_price:.2f}</b>"
    )


def generate_slow_path_confirmation_text(user_data: dict, cart: CartDTO) -> str:
    """Generate confirmation text for slow path checkout."""
    return (
        "<b>Please confirm your details:</b>\n\n"
        f"<b>Contact:</b> {escape(user_data['name'])}, {escape(user_data['phone'])}\n"
        f"<b>Shipping to:</b>\n<code>{escape(user_data['address'])}</code>\n\n"
        f"<b>Total Price: ${cart.total_price:.2f}</b>"
    )
