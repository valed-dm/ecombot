"""Product and category catalog CRUD operations."""

from decimal import Decimal
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...logging_setup import log
from ..models import CartItem
from ..models import Category
from ..models import OrderItem
from ..models import Product


async def get_categories(session: AsyncSession) -> List[Category]:
    """Fetches all top-level categories."""
    stmt = select(Category).where(Category.parent_id.is_(None)).order_by(Category.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_name(session: AsyncSession, name: str) -> Optional[Category]:
    """Fetches a category by its exact name."""
    stmt = select(Category).where(Category.name == name)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_category(
    session: AsyncSession,
    name: str,
    description: Optional[str] = None,
) -> Category:
    """Creates a new category in the database."""
    new_category = Category(name=name, description=description)
    session.add(new_category)
    await session.flush()
    return new_category


async def delete_category_if_empty(
    session: AsyncSession, category_id: int
) -> tuple[bool, bool]:
    """
    Atomically checks if a category is empty and deletes it if so.
    Returns (deleted, category_exists) tuple.
    """
    # First check if category exists
    category = await session.get(Category, category_id)
    if not category:
        return False, False  # Not deleted, doesn't exist

    # Check for products in the category within the same transaction
    stmt = select(Product).where(Product.category_id == category_id).limit(1)
    result = await session.execute(stmt)
    if result.scalars().first():
        return False, True  # Not deleted, exists but has products

    # Category exists and is empty, delete it using direct SQL
    delete_stmt = delete(Category).where(Category.id == category_id)
    await session.execute(delete_stmt)
    await session.flush()

    return True, True  # Deleted successfully


async def get_product(session: AsyncSession, product_id: int) -> Optional[Product]:
    """
    Fetches a single product by its ID, eagerly loading its category.
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_products_by_category(
    session: AsyncSession, category_id: int
) -> List[Product]:
    """
    Fetches all products within a specific category.
    Note: Category relationship is eagerly loaded despite redundancy
    to avoid lazy loading issues during DTO conversion.
    """
    stmt = (
        select(Product)
        .where(Product.category_id == category_id)
        .options(selectinload(Product.category))
        .order_by(Product.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: Decimal,
    stock: int,
    category_id: int,
    image_url: Optional[str] = None,
) -> Product:
    """Creates a new product in the database."""
    # Validate business rules
    if price <= 0:
        log.warning(f"Attempt to create product '{name}' with invalid price: {price}")
        raise ValueError("Price must be positive")

    if stock < 0:
        log.warning(f"Attempt to create product '{name}' with invalid stock: {stock}")
        raise ValueError("Stock must be non-negative")

    # Validate category exists
    category = await session.get(Category, category_id)
    if not category:
        log.warning(
            f"Attempt to create product '{name}' with non-existent "
            f"category_id: {category_id}"
        )
        raise ValueError(f"Category with ID {category_id} does not exist")

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        image_url=image_url,
    )
    session.add(new_product)
    await session.flush()
    return new_product


async def update_product(
    session: AsyncSession, product_id: int, update_data: Dict[str, Any]
) -> Optional[Product]:
    """
    Updates a product's details and returns the updated object with
    all necessary relationships eagerly loaded for DTO conversion.
    """
    allowed_fields = {"name", "description", "price", "stock", "image_url"}

    filtered_data = {}
    for key, value in update_data.items():
        if key in allowed_fields:
            filtered_data[key] = value
        else:
            log.warning(
                f"Attempt to update invalid product field '{key}' "
                f"for product {product_id}"
            )

    if not filtered_data:
        return await get_product(session, product_id)

    # Validate business rules for updates
    if "price" in filtered_data and filtered_data["price"] <= 0:
        log.warning(
            f"Attempt to update product {product_id} with invalid price: "
            f"{filtered_data['price']}"
        )
        raise ValueError("Price must be positive")

    if "stock" in filtered_data and filtered_data["stock"] < 0:
        log.warning(
            f"Attempt to update product {product_id} with invalid stock: "
            f"{filtered_data['stock']}"
        )
        raise ValueError("Stock must be non-negative")

    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(**filtered_data)
        .returning(Product.id)
    )
    result = await session.execute(stmt)
    updated_id = result.scalar_one_or_none()

    if updated_id:
        return await get_product(session, updated_id)

    return None


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Deletes a product from the database by its ID using direct SQL."""
    # First check if product exists and get image path
    product = await session.get(Product, product_id)
    if not product:
        return False

    image_path = product.image_url  # Store image path before deletion

    # Remove product from all carts first (to handle foreign key constraints)
    cart_delete_stmt = delete(CartItem).where(CartItem.product_id == product_id)
    await session.execute(cart_delete_stmt)

    # Check for order items (prevent deletion of historical records)
    order_items_stmt = (
        select(OrderItem).where(OrderItem.product_id == product_id).limit(1)
    )
    order_result = await session.execute(order_items_stmt)
    if order_result.scalars().first():
        log.warning(f"Cannot delete product {product_id}: has order history")
        return False

    # Delete the product using direct SQL
    product_delete_stmt = delete(Product).where(Product.id == product_id)
    result = await session.execute(product_delete_stmt)
    await session.flush()

    # Clean up image file if product was successfully deleted
    if result.rowcount > 0 and image_path:
        try:
            Path(image_path).unlink(missing_ok=True)
            log.info(f"Deleted product image: {image_path}")
        except OSError as e:
            log.error(f"Failed to delete image file {image_path}: {e}")

    return result.rowcount > 0
