"""Product and category catalog CRUD operations."""

from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...logging_setup import log
from ..models import CartItem
from ..models import Category
from ..models import Product


async def get_categories(session: AsyncSession) -> List[Category]:
    """Fetches all active (non-deleted) top-level categories."""
    stmt = (
        select(Category)
        .where(Category.parent_id.is_(None), Category.deleted_at.is_(None))
        .order_by(Category.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_name(session: AsyncSession, name: str) -> Optional[Category]:
    """Fetches an active (non-deleted) category by its exact name."""
    stmt = select(Category).where(Category.name == name, Category.deleted_at.is_(None))
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


async def soft_delete_category(session: AsyncSession, category_id: int) -> bool:
    """
    Soft deletes a category by setting deleted_at timestamp.
    Also cascades to soft delete all products and subcategories.
    Returns True if category was found and soft deleted.
    """
    # Check if category exists and is not already deleted
    category = await session.get(Category, category_id)
    if not category or category.deleted_at is not None:
        return False

    # Cascade soft delete to all products in this category
    products_stmt = (
        update(Product)
        .where(Product.category_id == category_id, Product.deleted_at.is_(None))
        .values(deleted_at=func.now())
    )
    await session.execute(products_stmt)

    # Remove products from carts (no longer available)
    cart_delete_stmt = delete(CartItem).where(
        CartItem.product_id.in_(
            select(Product.id).where(Product.category_id == category_id)
        )
    )
    await session.execute(cart_delete_stmt)

    # Cascade soft delete to all subcategories
    subcategories_stmt = (
        update(Category)
        .where(Category.parent_id == category_id, Category.deleted_at.is_(None))
        .values(deleted_at=func.now())
    )
    await session.execute(subcategories_stmt)

    # Finally, soft delete the category itself
    stmt = (
        update(Category).where(Category.id == category_id).values(deleted_at=func.now())
    )
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount > 0


async def get_product(session: AsyncSession, product_id: int) -> Optional[Product]:
    """
    Fetches a single active (non-deleted) product by its ID,
    eagerly loading its category.
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id, Product.deleted_at.is_(None))
        .options(selectinload(Product.category))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_products_by_category(
    session: AsyncSession, category_id: int
) -> List[Product]:
    """
    Fetches all active (non-deleted) products within a specific category.
    Note: Category relationship is eagerly loaded despite redundancy
    to avoid lazy loading issues during DTO conversion.
    """
    stmt = (
        select(Product)
        .where(Product.category_id == category_id, Product.deleted_at.is_(None))
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


async def get_product_including_deleted(
    session: AsyncSession, product_id: int
) -> Optional[Product]:
    """
    Fetches a product by ID including soft-deleted ones (for order history).
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_category_including_deleted(
    session: AsyncSession, category_id: int
) -> Optional[Category]:
    """
    Fetches a category by ID including soft-deleted ones (for order history).
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def soft_delete_product(session: AsyncSession, product_id: int) -> bool:
    """
    Soft deletes a product by setting deleted_at timestamp.
    Also removes product from all carts since it's no longer available.
    Returns True if product was found and soft deleted.
    """
    # Check if product exists and is not already deleted
    product = await session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        return False

    # Remove product from all carts (no longer available for purchase)
    cart_delete_stmt = delete(CartItem).where(CartItem.product_id == product_id)
    await session.execute(cart_delete_stmt)

    # Soft delete the product
    stmt = update(Product).where(Product.id == product_id).values(deleted_at=func.now())
    result = await session.execute(stmt)
    await session.flush()

    return result.rowcount > 0


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Soft deletes a product (replaces hard delete)."""
    return await soft_delete_product(session, product_id)
