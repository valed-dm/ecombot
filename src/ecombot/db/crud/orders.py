"""Order management CRUD operations."""

from typing import List, Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...logging_setup import log
from ...schemas.enums import OrderStatus
from ...utils import generate_order_number
from ..models import CartItem, Order, OrderItem, Product


async def create_order_with_items(
    session: AsyncSession,
    user_id: int,
    contact_name: str,
    phone: str,
    address: str,
    delivery_method: str,
    items: List[CartItem],
) -> Order:
    """
    Creates an order from cart items and atomically reserves stock.
    This is the core transactional function.
    """
    new_order = Order(
        user_id=user_id,
        order_number=generate_order_number(),
        contact_name=contact_name,
        phone=phone,
        address=address,
        delivery_method=delivery_method,
    )
    session.add(new_order)
    await session.flush()

    for item in items:
        product_id = item.product_id
        quantity = item.quantity

        # Get the product with a pessimistic lock.
        product = await session.get(Product, product_id, with_for_update=True)

        if product is None:
            raise ValueError(f"Product with ID {product_id} not found during checkout.")
        if product.stock < quantity:
            raise ValueError(
                f"Not enough stock for '{product.name}'. "
                f"You requested {quantity}, but only {product.stock} are available."
            )

        new_order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
        )
        session.add(new_order_item)

        product.stock -= quantity

    return new_order


async def get_order(session: AsyncSession, order_id: int) -> Optional[Order]:
    """Fetches a single order by its ID, loading its items."""
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.user),
            selectinload(Order.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.category),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_orders_by_user_pk(
    session: AsyncSession,
    user_id: int,
) -> Sequence[Order]:
    """
    Fetches all of a user's orders by their user primary key,
    eagerly loading all nested relationships needed for DTO conversion.
    """
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.user),
            selectinload(Order.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.category),
        )
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_orders_by_status(
    session: AsyncSession,
    status: OrderStatus,
) -> Sequence[Order]:
    """Fetches all orders with a specific status."""
    stmt = (
        select(Order)
        .where(Order.status == status)
        .options(
            selectinload(Order.user),
            selectinload(Order.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.category),
        )
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_order_status(
    session: AsyncSession,
    order_id: int,
    new_status: OrderStatus,
) -> Optional[Order]:
    """Updates the status of a specific order."""
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .values(status=new_status)
        .returning(Order.id)
    )
    result = await session.execute(stmt)
    updated_id = result.scalar_one_or_none()

    if updated_id:
        await session.flush()
        return await get_order(session, updated_id)
    return None


async def restore_stock_for_order_items(
    session: AsyncSession,
    order_items: List[OrderItem],
) -> None:
    """
    Atomically restores stock for all items in an order using pessimistic locking.
    Similar to create_order_with_items but for stock restoration.
    """
    for item in order_items:
        # Get the product with a pessimistic lock
        product = await session.get(Product, item.product_id, with_for_update=True)
        if product:
            product.stock += item.quantity
        else:
            log.warning(
                f"Product with ID {item.product_id} not found during "
                f"stock restoration. Product may have been deleted after "
                f"order was placed."
            )

    await session.flush()