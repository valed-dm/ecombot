"""Common utilities for checkout process."""

from html import escape
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.config import settings
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import DeliveryOption
from ecombot.db.models import PickupPoint
from ecombot.db.models import User
from ecombot.schemas.dto import CartDTO
from ecombot.schemas.enums import DeliveryType


def get_default_address(user: User) -> Optional[DeliveryAddress]:
    """Get user's default delivery address."""
    return next((addr for addr in user.addresses if addr.is_default), None)


def determine_missing_info(
    user: User,
    default_address: Optional[DeliveryAddress],
    courier_available: bool = False,
) -> list[str]:
    """Determine what information is missing for checkout."""
    missing_info = []
    if not user.phone:
        missing_info.append(manager.get_message("checkout", "missing_phone"))

    # Only check for address if courier delivery is available
    if courier_available and not default_address:
        missing_info.append(manager.get_message("checkout", "missing_address"))
    return missing_info


async def check_courier_availability(session: AsyncSession) -> bool:
    """
    Checks if courier delivery is available.
    Returns True if global DELIVERY is True AND there is at least one active
    DeliveryOption that is NOT a pickup type.
    """
    if not settings.DELIVERY:
        return False

    pickup_types = [
        DeliveryType.PICKUP_STORE,
        DeliveryType.PICKUP_LOCKER,
        DeliveryType.PICKUP_CURBSIDE,
    ]
    stmt = select(DeliveryOption).where(
        DeliveryOption.is_active,
        DeliveryOption.delivery_type.notin_(pickup_types),
    )
    result = await session.execute(stmt)
    return bool(result.scalars().first())


async def get_active_pickup_points(session: AsyncSession) -> list[PickupPoint]:
    """Returns a list of all active pickup points."""
    stmt = select(PickupPoint).where(PickupPoint.is_active)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def generate_fast_path_confirmation_text(
    user: User,
    default_address: Optional[DeliveryAddress],
    cart: CartDTO,
    is_pickup: bool = False,
    pickup_point: Optional[PickupPoint] = None,
) -> str:
    """Generate confirmation text for fast path checkout."""
    currency = manager.get_message("common", "currency_symbol")

    if not is_pickup:
        address_text = escape(default_address.full_address) if default_address else ""
        msg = manager.get_message(
            "checkout",
            "fast_path_confirm",
            address=address_text,
            phone=escape(user.phone or "Not set"),
        )
    else:
        pp_text = (
            f"{pickup_point.name} ({pickup_point.address})"
            if pickup_point
            else "Pickup"
        )
        msg = manager.get_message(
            "checkout",
            "pickup_fast_confirm",
            phone=escape(user.phone or "Not set"),
            address=escape(pp_text),
        )

    return msg + f"\n\n<b>Total Price: {currency}{cart.total_price:.2f}</b>"


def generate_slow_path_confirmation_text(
    user_data: dict, cart: CartDTO, is_pickup: bool = False
) -> str:
    """Generate confirmation text for slow path checkout."""
    if not is_pickup:
        msg = manager.get_message(
            "checkout",
            "slow_path_confirm",
            name=escape(user_data.get("name", "")),
            phone=escape(user_data.get("phone", "")),
            address=escape(user_data.get("address", "")),
        )
    else:
        pp_name = user_data.get("pickup_point_name", "Pickup")
        msg = manager.get_message(
            "checkout",
            "pickup_slow_confirm",
            name=escape(user_data.get("name", "")),
            phone=escape(user_data.get("phone", "")),
            address=escape(pp_name),
        )

    return (
        msg
        + "\n\n"
        + manager.get_message("checkout", "total_price_line", total=cart.total_price)
    )
