"""
Service layer for shopping cart operations.
"""

from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.db import crud
from ecombot.schemas.dto import CartDTO


class ProductNotFoundError(Exception):
    """Raised when a product with the given ID does not exist."""

    pass


class InsufficientStockError(Exception):
    """Raised when trying to add more items to a cart than are in stock."""

    pass


class CartItemNotFoundError(Exception):
    """Raised when a cart item is not found or does not belong to the user."""

    pass


async def get_user_cart(session: AsyncSession, user_id: int) -> CartDTO:
    """
    Gets the user's current cart, creating one if necessary.
    Returns a DTO representing the cart's state.
    """
    db_cart = await crud.get_or_create_cart(session, user_id)
    return CartDTO.model_validate(db_cart)


async def add_product_to_cart(
    session: AsyncSession, user_id: int, product_id: int, quantity: int = 1
) -> CartDTO:
    """
    Adds a specified quantity of a product to the user's cart.
    This is a complete "unit of work" and handles its own transaction.
    """
    product = await crud.get_product(session, product_id)
    if not product:
        raise ProductNotFoundError(f"Product with ID {product_id} not found.")

    if product.stock < quantity:
        raise InsufficientStockError(f"Not enough stock for '{product.name}'.")

    # Get the user's cart using "lean" function.
    cart = await crud.get_or_create_cart_lean(session, user_id)

    await crud.add_item_to_cart(
        session=session, cart=cart, product=product, quantity=quantity
    )

    # Get the fully-loaded object for the DTO.
    fresh_cart_for_dto = await crud.get_or_create_cart(session, user_id)

    return CartDTO.model_validate(fresh_cart_for_dto)


async def alter_item_quantity(
    session: AsyncSession,
    user_id: int,
    cart_item_id: int,
    action: Literal["increase", "decrease", "remove"],
) -> CartDTO:
    """
    Service-level function to alter an item's quantity in the cart.
    - 'increase': Adds 1 to the quantity.
    - 'decrease': Subtracts 1 from the quantity.
    - 'remove': Sets the quantity to 0, effectively deleting the item.
    """
    cart = await crud.get_or_create_cart(session, user_id)

    item_to_update = None
    for item in cart.items:
        if item.id == cart_item_id:
            item_to_update = item
            break

    if not item_to_update:
        raise CartItemNotFoundError("Item not found in your cart.")

    new_quantity = item_to_update.quantity
    if action == "increase":
        new_quantity += 1
    elif action == "decrease":
        new_quantity -= 1
    elif action == "remove":
        new_quantity = 0

    try:
        await crud.set_cart_item_quantity(session, cart_item_id, new_quantity)
        fresh_cart = await crud.get_or_create_cart(session, user_id)
        return CartDTO.model_validate(fresh_cart)
    except Exception:
        raise


async def clear_user_cart(session: AsyncSession, user_id: int) -> None:
    """Clears all items from a user's cart."""
    cart = await crud.get_or_create_cart(session, user_id)
    await crud.clear_cart(session, cart)
