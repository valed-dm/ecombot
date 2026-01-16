"""
Service layer for order processing and management.
"""

from decimal import Decimal
from typing import List
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.db import crud
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import DeliveryOption
from ecombot.db.models import PickupPoint
from ecombot.db.models import User
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import DeliveryType
from ecombot.schemas.enums import OrderStatus


class OrderPlacementError(Exception):
    """Base exception for issues during order placement."""

    pass


class EmptyCartError(OrderPlacementError):
    """Raised when trying to place an order with an empty cart."""

    def __init__(self, message="Cannot place an order with an empty cart."):
        super().__init__(message)


class OrderNotFoundError(Exception):
    """Raised when an order with the given ID does not exist."""

    pass


async def place_order_from_cart(
    session: AsyncSession,
    user_id: int,
    contact_name: str,
    phone: str,
    delivery_type: DeliveryType,
    address: str | None = None,
    delivery_option_id: int | None = None,
    pickup_point_id: int | None = None,
) -> OrderDTO:
    """
    Handles the core business logic of placing an order.

    This is a complete transactional unit of work. It will:
    1. Retrieve the user's cart.
    2. Validate that the cart is not empty.
    3. Call the transactional CRUD function to create the order and reserve stock.
    4. Clear the user's cart upon success.
    5. Commit the entire transaction or roll it back upon failure.

    Args:
        session: The active SQLAlchemy AsyncSession.
        user_id: The ID of the user placing the order.
        contact_name: The customer's name for the order.
        phone: The customer's phone number.
        delivery_type: The chosen delivery type (Enum).
        address: The shipping address string (required if not pickup).
        delivery_option_id: ID of the selected delivery option (for fee calc).
        pickup_point_id: ID of the selected pickup point (required if pickup).

    Returns:
        An OrderDTO of the newly created order.

    Raises:
        EmptyCartError: If the user's cart has no items.
        OrderPlacementError: For stock-related or other database errors.
    """
    cart = await crud.get_or_create_cart(session, user_id)

    if not cart.items:
        raise EmptyCartError()

    # --- Validation & Fee Calculation ---
    delivery_fee = Decimal("0.00")
    final_address = address

    # 1. Validate Pickup vs Delivery
    is_pickup = delivery_type in (
        DeliveryType.PICKUP_STORE,
        DeliveryType.PICKUP_LOCKER,
        DeliveryType.PICKUP_CURBSIDE,
    )

    if is_pickup:
        if not pickup_point_id:
            raise OrderPlacementError(
                "A pickup point must be selected for pickup orders."
            )
        # Fetch pickup point to ensure it exists and get its address
        pickup_point = await session.get(PickupPoint, pickup_point_id)
        if not pickup_point:
            raise OrderPlacementError("Selected pickup point not found.")
        final_address = f"{pickup_point.name}: {pickup_point.address}"
    else:
        if not final_address:
            raise OrderPlacementError(
                "A delivery address is required for this delivery method."
            )

    # 2. Calculate Fee based on DeliveryOption
    if delivery_option_id:
        option = await session.get(DeliveryOption, delivery_option_id)
        if option:
            # Calculate cart total to check for free threshold
            cart_total = sum(
                (item.product.price * item.quantity for item in cart.items),
                start=Decimal("0.00"),
            )

            if option.free_threshold and cart_total >= option.free_threshold:
                delivery_fee = Decimal("0.00")
            else:
                delivery_fee = option.price

    try:
        # Pessimistic locking.
        order = await crud.create_order_with_items(
            session=session,
            user_id=user_id,
            contact_name=contact_name,
            phone=phone,
            address=final_address,
            delivery_type=delivery_type,
            delivery_option_id=delivery_option_id,
            pickup_point_id=pickup_point_id,
            delivery_fee=delivery_fee,
            items=list(cart.items),  # Copy of the items
        )

        await crud.clear_cart(session, cart)

        refreshed_order = await crud.get_order(session, order.id)
        if not refreshed_order:
            raise OrderPlacementError(
                "Failed to retrieve the order immediately after creation."
            )

        return OrderDTO.model_validate(refreshed_order)

    except ValueError as e:
        # "Not enough stock" error from crud.py
        raise OrderPlacementError(str(e)) from e
    except Exception as e:
        raise OrderPlacementError(
            f"An unexpected error occurred during checkout: {e}"
        ) from e


async def place_order(
    session: AsyncSession,
    db_user: User,
    delivery_type: DeliveryType,
    delivery_address: Optional[DeliveryAddress] = None,
    delivery_option_id: int | None = None,
    pickup_point_id: int | None = None,
) -> OrderDTO:
    """
    The main business logic for placing an order using pre-existing user data.
    """
    cart = await crud.get_or_create_cart(session, db_user.telegram_id)
    if not cart.items:
        raise EmptyCartError("Cannot place an order with an empty cart.")

    contact_name = db_user.first_name
    phone = db_user.phone

    if not phone:
        raise OrderPlacementError("User profile is incomplete. Phone is required.")

    # --- Validation & Fee Calculation ---
    delivery_fee = Decimal("0.00")
    final_address = delivery_address.full_address if delivery_address else None

    is_pickup = delivery_type in (
        DeliveryType.PICKUP_STORE,
        DeliveryType.PICKUP_LOCKER,
        DeliveryType.PICKUP_CURBSIDE,
    )

    if is_pickup:
        if not pickup_point_id:
            raise OrderPlacementError(
                "A pickup point must be selected for pickup orders."
            )
        pickup_point = await session.get(PickupPoint, pickup_point_id)
        if not pickup_point:
            raise OrderPlacementError("Selected pickup point not found.")
        final_address = f"{pickup_point.name}: {pickup_point.address}"
    else:
        if not final_address:
            raise OrderPlacementError(
                "User profile is incomplete. Address is required for delivery."
            )

    if delivery_option_id:
        option = await session.get(DeliveryOption, delivery_option_id)
        if option:
            # Calculate cart total
            cart_total = sum(
                (item.product.price * item.quantity for item in cart.items),
                start=Decimal("0.00"),
            )
            if option.free_threshold and cart_total >= option.free_threshold:
                delivery_fee = Decimal("0.00")
            else:
                delivery_fee = option.price

    try:
        order = await crud.create_order_with_items(
            session=session,
            user_id=db_user.id,
            contact_name=contact_name,
            phone=phone,
            address=final_address,
            delivery_type=delivery_type,
            delivery_option_id=delivery_option_id,
            pickup_point_id=pickup_point_id,
            delivery_fee=delivery_fee,
            items=list(cart.items),
        )
        await crud.clear_cart(session, cart)

        refreshed_order = await crud.get_order(session, order.id)
        if not refreshed_order:
            raise OrderPlacementError("Failed to retrieve order after creation.")
        return OrderDTO.model_validate(refreshed_order)

    except ValueError as e:
        raise OrderPlacementError(str(e)) from e
    except Exception as e:
        raise OrderPlacementError(
            f"An unexpected error occurred during checkout: {e}"
        ) from e


async def get_order_details(
    session: AsyncSession,
    order_id: int,
    user_id: int,
) -> Optional[OrderDTO]:
    """
    Fetches the details for a specific order, ensuring the user is authorized.
    Returns None if the order doesn't exist or doesn't belong to the user.
    """
    order = await crud.get_order(session, order_id)
    if not order or order.user_id != user_id:
        return None

    return OrderDTO.model_validate(order)


async def list_user_orders(session: AsyncSession, user_id: int) -> List[OrderDTO]:
    """
    Fetches a list of all orders placed by a specific user.
    Note: This will require a new CRUD function.
    """
    db_orders = await crud.get_orders_by_user_pk(session, user_id)
    return [OrderDTO.model_validate(order) for order in db_orders]


async def get_orders_by_status_for_admin(
    session: AsyncSession, status: OrderStatus
) -> List[OrderDTO]:
    """Admin service to get orders by status."""
    db_orders = await crud.get_orders_by_status(session, status)
    return [OrderDTO.model_validate(order) for order in db_orders]


async def change_order_status(
    session: AsyncSession, order_id: int, new_status: OrderStatus
) -> OrderDTO:
    """
    Admin service to change an order's status.

    Includes special business logic: if an order is cancelled, the stock for
    the items in that order is returned to the inventory.
    """
    order_to_update = await crud.get_order(session, order_id)
    if not order_to_update:
        raise OrderPlacementError("Order not found.")

    if new_status in [
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.FAILED,
    ]:
        # If moving TO a cancelled-like state, check if we are already in a
        # terminal state
        if order_to_update.status in [
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED,
            OrderStatus.FAILED,
        ]:
            raise OrderPlacementError(
                f"Cannot cancel a {order_to_update.status.value} order."
            )

        # Atomically restore stock for all items with pessimistic locking
        await crud.restore_stock_for_order_items(
            session=session, order_items=order_to_update.items
        )

    order_to_update.status = new_status
    await session.flush()

    refreshed_order = await crud.get_order(session, order_to_update.id)
    if not refreshed_order:
        raise OrderPlacementError("Failed to retrieve order after status update.")

    return OrderDTO.model_validate(refreshed_order)
