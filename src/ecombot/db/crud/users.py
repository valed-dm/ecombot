"""User and delivery address CRUD operations."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import aiogram
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...logging_setup import log
from ..models import DeliveryAddress
from ..models import User


async def get_or_create_user(
    session: AsyncSession, telegram_user: "aiogram.types.User"
) -> User:
    """
    Gets a user from the DB by their Telegram ID, creating one
    if they don't exist.
    """
    stmt = (
        select(User)
        .where(User.telegram_id == telegram_user.id)
        .options(selectinload(User.addresses))
    )
    result = await session.execute(stmt)
    db_user = result.scalars().first()

    if not db_user:
        db_user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.full_name,
        )
        session.add(db_user)
        await session.flush()
        await session.refresh(db_user, attribute_names=["addresses"])

    return db_user


async def update_user_profile(
    session: AsyncSession,
    user_id: int,
    update_data: Dict[str, Any],
) -> Optional[User]:
    """Updates a user's profile details (phone, email)."""
    allowed_fields = {"phone", "email", "first_name"}

    user = await session.get(User, user_id)
    if user:
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)
            else:
                log.warning(
                    f"Attempt to update invalid field '{key}' for user {user_id}"
                )
        await session.flush()
    return user


async def get_user_addresses(
    session: AsyncSession,
    user_id: int,
) -> List[DeliveryAddress]:
    """Fetches all saved delivery addresses for a specific user."""
    stmt = (
        select(DeliveryAddress)
        .where(DeliveryAddress.user_id == user_id)
        .order_by(DeliveryAddress.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def add_delivery_address(
    session: AsyncSession,
    user_id: int,
    label: str,
    address: str,
) -> DeliveryAddress:
    """Adds a new delivery address for a user."""
    new_address = DeliveryAddress(
        user_id=user_id,
        address_label=label,
        full_address=address,
    )
    session.add(new_address)
    await session.flush()
    return new_address


async def delete_delivery_address(
    session: AsyncSession,
    address_id: int,
    user_id: int,
) -> bool:
    """
    Deletes a delivery address, ensuring it belongs to the correct user.
    """
    address = await session.get(DeliveryAddress, address_id)
    if address and address.user_id == user_id:
        session.delete(address)
        await session.flush()
        return True
    return False


async def set_default_address(
    session: AsyncSession, user_id: int, address_id: int
) -> Optional[DeliveryAddress]:
    """Sets a specific address as the default for the user."""
    # Step 1: Set all the user's other addresses to is_default = False
    update_stmt = (
        update(DeliveryAddress)
        .where(DeliveryAddress.user_id == user_id, DeliveryAddress.id != address_id)
        .values(is_default=False)
    )
    await session.execute(update_stmt)

    # Step 2: Get the target address and set it as the default
    address_to_set = await session.get(DeliveryAddress, address_id)
    if address_to_set and address_to_set.user_id == user_id:
        address_to_set.is_default = True
        await session.flush()
        return address_to_set
    return None
