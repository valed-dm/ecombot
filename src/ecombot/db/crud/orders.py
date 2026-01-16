"""Order management CRUD operations."""

from decimal import Decimal
from typing import List
from typing import Optional
from typing import Sequence

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...logging_setup import log
from ...schemas.enums import DeliveryType
from ...schemas.enums import OrderStatus
from ...utils import generate_order_number
from ..models import CartItem
from ..models import Order
from ..models import OrderItem
from ..models import Product


class InsufficientStockError(Exception):
    """Raised when trying to order more items than are in stock."""

    pass


async def create_order_with_items(
    session: AsyncSession,
    user_id: int,
    contact_name: str,
    phone: str,
    address: Optional[str],
    delivery_type: DeliveryType,
    delivery_option_id: Optional[int],
    pickup_point_id: Optional[int],
    delivery_fee: Decimal,
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
        delivery_type=delivery_type,
        delivery_option_id=delivery_option_id,
        pickup_point_id=pickup_point_id,
        delivery_fee=delivery_fee,
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
            raise InsufficientStockError(
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
    """Fetches a single order by its ID, loading its items with products
    (including deleted)."""
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.user),
            selectinload(Order.items),
            selectinload(Order.pickup_point),
        )
    )
    result = await session.execute(stmt)
    order = result.scalars().first()

    if order:
        # Manually load products including deleted ones
        for item in order.items:
            product_stmt = (
                select(Product)
                .where(Product.id == item.product_id)
                .options(selectinload(Product.category))
            )
            product_result = await session.execute(product_stmt)
            item.product = product_result.scalars().first()

    return order


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
            selectinload(Order.items),
            selectinload(Order.pickup_point),
        )
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()

    # Manually load products including deleted ones
    for order in orders:
        for item in order.items:
            product_stmt = (
                select(Product)
                .where(Product.id == item.product_id)
                .options(selectinload(Product.category))
            )
            product_result = await session.execute(product_stmt)
            item.product = product_result.scalars().first()

    return orders


async def get_orders_by_status(
    session: AsyncSession,
    status: OrderStatus,
) -> Sequence[Order]:
    """Fetches all orders with a specific status, including deleted products."""
    stmt = (
        select(Order)
        .where(Order.status == status)
        .options(
            selectinload(Order.user),
            selectinload(Order.items),
            selectinload(Order.pickup_point),
        )
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()

    # Manually load products including deleted ones
    for order in orders:
        for item in order.items:
            product_stmt = (
                select(Product)
                .where(Product.id == item.product_id)
                .options(selectinload(Product.category))
            )
            product_result = await session.execute(product_stmt)
            item.product = product_result.scalars().first()

    return orders


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
