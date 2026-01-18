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
from ..models import OrderItem
from ..models import Product
from ..models import ProductImage


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
    Also cascades to soft delete all products and subcategories, restoring stock.
    Returns True if category was found and soft deleted.
    """
    # Check if category exists and is not already deleted
    category = await session.get(Category, category_id)
    if not category or category.deleted_at is not None:
        return False

    # Get all products in this category that are active
    products_stmt = select(Product.id).where(
        Product.category_id == category_id, Product.deleted_at.is_(None)
    )
    products_result = await session.execute(products_stmt)
    product_ids = [row[0] for row in products_result.fetchall()]

    # For each product, calculate sold quantity and restore stock
    for product_id in product_ids:
        sold_quantity_stmt = select(
            func.coalesce(func.sum(OrderItem.quantity), 0)
        ).where(OrderItem.product_id == product_id)
        sold_result = await session.execute(sold_quantity_stmt)
        total_sold = sold_result.scalar() or 0

        # Update product: soft delete and restore stock
        product_update_stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(deleted_at=func.now(), stock=Product.stock + total_sold)
        )
        await session.execute(product_update_stmt)

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
    eagerly loading its category and images.
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id, Product.deleted_at.is_(None))
        .options(selectinload(Product.category), selectinload(Product.images))
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
        .options(selectinload(Product.category), selectinload(Product.images))
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
    images: Optional[List[str]] = None,
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
    )
    session.add(new_product)
    await session.flush()

    if images:
        for i, file_id in enumerate(images):
            session.add(
                ProductImage(
                    product_id=new_product.id, file_id=file_id, is_main=(i == 0)
                )
            )
        await session.flush()
    return new_product


async def update_product(
    session: AsyncSession, product_id: int, update_data: Dict[str, Any]
) -> Optional[Product]:
    """
    Updates a product's details and returns the updated object with
    all necessary relationships eagerly loaded for DTO conversion.
    """
    allowed_fields = {"name", "description", "price", "stock"}

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


async def add_product_image(
    session: AsyncSession, product_id: int, file_id: str, is_main: bool = False
) -> ProductImage:
    """Adds a new image to a product, avoiding duplicates."""
    # Check if image already exists
    stmt = select(ProductImage).where(
        ProductImage.product_id == product_id, ProductImage.file_id == file_id
    )
    result = await session.execute(stmt)
    existing_image = result.scalars().first()

    if existing_image:
        return existing_image

    # If not explicitly set as main, check if the product has any main image
    if not is_main:
        stmt_main = select(ProductImage).where(
            ProductImage.product_id == product_id, ProductImage.is_main.is_(True)
        )
        result_main = await session.execute(stmt_main)
        if not result_main.scalars().first():
            is_main = True

    new_image = ProductImage(product_id=product_id, file_id=file_id, is_main=is_main)
    session.add(new_image)
    await session.flush()
    return new_image


async def update_product_image_telegram_id(
    session: AsyncSession, image_id: int, telegram_file_id: str
) -> None:
    """Updates the cached telegram_file_id of a product image."""
    stmt = (
        update(ProductImage)
        .where(ProductImage.id == image_id)
        .values(telegram_file_id=telegram_file_id)
    )
    await session.execute(stmt)
    await session.flush()


async def delete_product_image(session: AsyncSession, image_id: int) -> bool:
    """Deletes a product image."""
    image = await session.get(ProductImage, image_id)
    if image:
        await session.delete(image)
        await session.flush()
        return True
    return False


async def get_product_including_deleted(
    session: AsyncSession, product_id: int
) -> Optional[Product]:
    """
    Fetches a product by ID including soft-deleted ones (for order history).
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category), selectinload(Product.images))
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
    Also removes product from all carts and restores stock from placed orders.
    Returns True if product was found and soft deleted.
    """
    # Check if product exists and is not already deleted
    product = await session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        return False

    # Calculate total quantity sold from orders and restore to stock
    sold_quantity_stmt = select(func.coalesce(func.sum(OrderItem.quantity), 0)).where(
        OrderItem.product_id == product_id
    )
    result = await session.execute(sold_quantity_stmt)
    total_sold = result.scalar() or 0

    # Remove product from all carts (no longer available for purchase)
    cart_delete_stmt = delete(CartItem).where(CartItem.product_id == product_id)
    await session.execute(cart_delete_stmt)

    # Soft delete the product and restore stock from orders
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(deleted_at=func.now(), stock=product.stock + total_sold)
    )
    result = await session.execute(stmt)
    await session.flush()

    return result.rowcount > 0


async def restore_category(session: AsyncSession, category_id: int) -> bool:
    """
    Restores a soft-deleted category by clearing deleted_at timestamp.
    Also restores all products and subcategories within it, including stock.
    Returns True if category was found and restored.
    """
    # Check if category exists and is soft-deleted
    category = await session.get(Category, category_id)
    if not category or category.deleted_at is None:
        return False

    # Restore the category itself
    stmt = update(Category).where(Category.id == category_id).values(deleted_at=None)
    result = await session.execute(stmt)

    # Get all products in this category that are soft-deleted
    products_stmt = select(Product.id).where(
        Product.category_id == category_id, Product.deleted_at.is_not(None)
    )
    products_result = await session.execute(products_stmt)
    product_ids = [row[0] for row in products_result.fetchall()]

    # Restore each product with stock calculation
    for product_id in product_ids:
        # Calculate total quantity sold from orders
        sold_quantity_stmt = select(
            func.coalesce(func.sum(OrderItem.quantity), 0)
        ).where(OrderItem.product_id == product_id)
        sold_result = await session.execute(sold_quantity_stmt)
        total_sold = sold_result.scalar() or 0

        # Get current stock and restore product with decreased stock
        product = await session.get(Product, product_id)
        if product:
            # Ensure stock doesn't go negative
            new_stock = max(0, product.stock - total_sold)
            restore_stmt = (
                update(Product)
                .where(Product.id == product_id)
                .values(deleted_at=None, stock=new_stock)
            )
            await session.execute(restore_stmt)

    # Restore all subcategories
    subcategories_stmt = (
        update(Category)
        .where(Category.parent_id == category_id, Category.deleted_at.is_not(None))
        .values(deleted_at=None)
    )
    await session.execute(subcategories_stmt)

    await session.flush()
    return result.rowcount > 0


async def restore_product(session: AsyncSession, product_id: int) -> bool:
    """
    Restores a soft-deleted product by clearing deleted_at timestamp.
    Also restores stock that was decremented from placed orders.
    Returns True if product was found and restored.
    """
    # Check if product exists and is soft-deleted
    product = await session.get(Product, product_id)
    if not product or product.deleted_at is None:
        return False

    # Calculate total quantity sold from orders while product was active
    sold_quantity_stmt = select(func.coalesce(func.sum(OrderItem.quantity), 0)).where(
        OrderItem.product_id == product_id
    )
    result = await session.execute(sold_quantity_stmt)
    total_sold = result.scalar() or 0

    # Restore the product and decrease stock for existing orders
    new_stock = max(0, product.stock - total_sold)  # Ensure stock doesn't go negative
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(deleted_at=None, stock=new_stock)
    )
    result = await session.execute(stmt)
    await session.flush()

    return result.rowcount > 0


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Soft deletes a product (replaces hard delete)."""
    return await soft_delete_product(session, product_id)


async def get_deleted_categories(session: AsyncSession) -> List[Category]:
    """Fetches all soft-deleted categories."""
    stmt = (
        select(Category).where(Category.deleted_at.is_not(None)).order_by(Category.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_deleted_products(session: AsyncSession) -> List[Product]:
    """Fetches all soft-deleted products with their categories."""
    stmt = (
        select(Product)
        .where(Product.deleted_at.is_not(None))
        .options(selectinload(Product.category), selectinload(Product.images))
        .order_by(Product.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
