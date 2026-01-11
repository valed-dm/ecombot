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
        missing_info.append(manager.get_message("checkout", "missing_phone"))
    if not default_address:
        missing_info.append(manager.get_message("checkout", "missing_address"))
    return missing_info


def generate_fast_path_confirmation_text(
    user: User, default_address: DeliveryAddress, cart: CartDTO
) -> str:
    """Generate confirmation text for fast path checkout."""
    currency = manager.get_message("common", "currency_symbol")
    return (
        manager.get_message(
            "checkout",
            "fast_path_confirm",
            address=escape(default_address.full_address or ""),
            phone=escape(user.phone or "Not set"),
        )
        + f"\n\n<b>Total Price: {currency}{cart.total_price:.2f}</b>"
    )


def generate_slow_path_confirmation_text(user_data: dict, cart: CartDTO) -> str:
    """Generate confirmation text for slow path checkout."""
    return (
        manager.get_message(
            "checkout",
            "slow_path_confirm",
            name=escape(user_data.get("name", "")),
            phone=escape(user_data.get("phone", "")),
            address=escape(user_data.get("address", "")),
        )
        + "\n\n"
        + manager.get_message("checkout", "total_price_line", total=cart.total_price)
    )
