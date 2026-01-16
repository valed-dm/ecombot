"""
CRUD operations for delivery management (Pickup Points and Delivery Options).
"""

from typing import Optional
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.db.models import DeliveryOption
from ecombot.db.models import PickupPoint
from ecombot.schemas.enums import DeliveryType


async def get_all_pickup_points(session: AsyncSession) -> Sequence[PickupPoint]:
    """Retrieves all pickup points ordered by ID."""
    stmt = select(PickupPoint).order_by(PickupPoint.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_pickup_point(
    session: AsyncSession, pickup_point_id: int
) -> Optional[PickupPoint]:
    """Retrieves a single pickup point by ID."""
    return await session.get(PickupPoint, pickup_point_id)


async def create_pickup_point(
    session: AsyncSession,
    name: str,
    address: str,
    pickup_type: DeliveryType,
    working_hours: Optional[str] = None,
) -> PickupPoint:
    """Creates a new pickup point."""
    new_pp = PickupPoint(
        name=name,
        address=address,
        pickup_type=pickup_type,
        working_hours=working_hours,
        is_active=True,
    )
    session.add(new_pp)
    await session.flush()
    return new_pp


async def toggle_pickup_point_status(
    session: AsyncSession, pickup_point_id: int
) -> Optional[PickupPoint]:
    """Toggles the active status of a pickup point."""
    pp = await session.get(PickupPoint, pickup_point_id)
    if pp:
        pp.is_active = not pp.is_active
        await session.flush()
    return pp


async def delete_pickup_point(session: AsyncSession, pickup_point_id: int) -> bool:
    """Deletes a pickup point."""
    pp = await session.get(PickupPoint, pickup_point_id)
    if pp:
        await session.delete(pp)
        await session.flush()
        return True
    return False


async def get_all_delivery_options(session: AsyncSession) -> Sequence[DeliveryOption]:
    """Retrieves all delivery options."""
    stmt = select(DeliveryOption)
    result = await session.execute(stmt)
    return result.scalars().all()


async def toggle_delivery_option(
    session: AsyncSession, delivery_type: DeliveryType
) -> DeliveryOption:
    """
    Toggles the active status of a delivery option.
    Creates it if it doesn't exist.
    """
    stmt = select(DeliveryOption).where(DeliveryOption.delivery_type == delivery_type)
    result = await session.execute(stmt)
    option = result.scalar_one_or_none()

    if option:
        option.is_active = not option.is_active
    else:
        option = DeliveryOption(
            delivery_type=delivery_type,
            name=delivery_type.value.replace("_", " ").title(),
            price=0,
            is_active=True,
        )
        session.add(option)

    await session.flush()
    return option
