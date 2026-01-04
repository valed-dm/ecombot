"""Shopping cart CRUD operations."""

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Cart
from ..models import CartItem
from ..models import Product


async def get_or_create_cart(session: AsyncSession, user_id: int) -> Cart:
    """
    Retrieves a user's cart, eagerly loading all nested relationships
    (items and their products) needed for DTO conversion.
    Creates a new cart if one doesn't exist.
    """
    stmt = (
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.product)
            .selectinload(Product.category)
        )
    )
    result = await session.execute(stmt)
    cart = result.scalars().first()

    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.flush()
        await session.refresh(cart, attribute_names=["items"])

    return cart


async def get_or_create_cart_lean(session: AsyncSession, user_id: int) -> Cart:
    """
    Retrieves a user's cart without any eager loading.
    Creates a new cart if one doesn't exist.
    This is optimized for operations that only need the cart ID.
    """
    stmt = select(Cart).where(Cart.user_id == user_id)
    result = await session.execute(stmt)
    cart = result.scalars().first()

    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.flush()

    return cart


async def add_item_to_cart(
    session: AsyncSession, cart: Cart, product: Product, quantity: int = 1
) -> CartItem:
    """Adds a product to the cart or updates its quantity if it already exists."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    stmt = select(CartItem).where(
        CartItem.cart_id == cart.id, CartItem.product_id == product.id
    )
    result = await session.execute(stmt)
    cart_item = result.scalars().first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        session.add(cart_item)

    await session.flush()
    return cart_item


async def set_cart_item_quantity(
    session: AsyncSession,
    cart_item_id: int,
    new_quantity: int,
) -> CartItem | None:
    """
    Sets the quantity of a specific cart item.
    If the quantity is 0 or less, the item is deleted.
    """
    if new_quantity < 0:
        raise ValueError("Quantity cannot be negative")

    if new_quantity > 100:
        raise ValueError("Quantity cannot exceed 100")

    cart_item = await session.get(CartItem, cart_item_id)
    if not cart_item:
        return None

    if new_quantity > 0:
        cart_item.quantity = new_quantity
        await session.flush()
        return cart_item
    else:
        # If quantity is 0 or less, delete the item using direct SQL.
        delete_stmt = delete(CartItem).where(CartItem.id == cart_item_id)
        await session.execute(delete_stmt)
        await session.flush()
        return None


async def clear_cart(session: AsyncSession, cart: Cart) -> None:
    """Removes all items from a user's cart."""
    stmt = delete(CartItem).where(CartItem.cart_id == cart.id)
    await session.execute(stmt)
    cart.items = []  # Keep object state in sync with database
    await session.flush()
