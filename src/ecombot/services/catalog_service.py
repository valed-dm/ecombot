"""
Service layer for catalog-related operations.
"""

from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.db import crud
from ecombot.logging_setup import log
from ecombot.schemas.dto import AdminProductDTO
from ecombot.schemas.dto import CategoryDTO
from ecombot.schemas.dto import ProductDTO
from ecombot.services.cart_service import ProductNotFoundError


class CategoryAlreadyExistsError(Exception):
    """Raised when trying to create a category that already exists."""

    pass


class CategoryNotEmptyError(Exception):
    """Raised when trying to delete a category that still contains products."""

    pass


async def get_all_categories(session: AsyncSession) -> List[CategoryDTO]:
    """
    Fetches all top-level product categories.
    Returns a list of DTOs, ready for the view layer.
    """
    db_categories = await crud.get_categories(session)
    return [CategoryDTO.model_validate(category) for category in db_categories]


async def get_products_in_category(
    session: AsyncSession, category_id: int
) -> List[ProductDTO]:
    """
    Fetches all products within a specific category.
    """
    db_products = await crud.get_products_by_category(session, category_id)
    return [ProductDTO.model_validate(product) for product in db_products]


async def add_new_category(
    session: AsyncSession, name: str, description: Optional[str] = None
) -> CategoryDTO:
    """
    Service-level function to add a new category.
    Enforces the business rule that category names must be unique.
    """
    existing_category = await crud.get_category_by_name(session, name)
    if existing_category:
        raise CategoryAlreadyExistsError(
            f"A category with the name '{name}' already exists."
        )

    category = await crud.create_category(session, name, description)
    return CategoryDTO.model_validate(category)


async def delete_category_by_id(session: AsyncSession, category_id: int) -> bool:
    """
    Service-level function to delete a category.
    Uses atomic operation to check for products and delete within the same transaction.
    """
    deleted, category_exists = await crud.delete_category_if_empty(session, category_id)

    if not category_exists:
        return False  # Category doesn't exist

    if not deleted:
        raise CategoryNotEmptyError(
            f"Cannot delete category ID {category_id} because it contains products."
        )

    return True


async def get_single_product_details(
    session: AsyncSession, product_id: int
) -> Optional[ProductDTO]:
    """
    Fetches the detailed information for a single product.
    Returns None if the product is not found.
    """
    db_product = await crud.get_product(session, product_id)
    if db_product:
        return ProductDTO.model_validate(db_product)
    return None


async def get_single_product_details_for_admin(
    session: AsyncSession,
    product_id: int,
) -> Optional[AdminProductDTO]:
    """
    Fetches the detailed information for a single product for the admin panel.
    Returns the more detailed AdminProductDTO.
    """
    db_product = await crud.get_product(session, product_id)
    if db_product:
        return AdminProductDTO.model_validate(db_product)
    return None


async def add_new_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: Decimal,
    stock: int,
    category_id: int,
    image_url: Optional[str] = None,
) -> ProductDTO:
    """
    Service-level function to handle the business logic of adding a new product.
    This is a complete unit of work.
    
    Note: The additional get_product call is necessary because ProductDTO requires
    the category relationship, which is not eagerly loaded by create_product.
    """
    try:
        product = await crud.create_product(
            session=session,
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image_url=image_url,
        )

        refreshed_product = await crud.get_product(session, product.id)
        if not refreshed_product:
            raise Exception("Failed to retrieve the product after creation.")

        return ProductDTO.model_validate(refreshed_product)

    except Exception as e:
        log.error("Failed to create product: {}", e)
        raise


async def update_product_details(
    session: AsyncSession,
    product_id: int,
    update_data: Dict[str, Any],
) -> AdminProductDTO:
    """
    Service-level function to update a product. Handles the transaction
    and returns the updated product as a DTO.
    """
    updated_product = await crud.update_product(
        session,
        product_id,
        update_data,
    )
    if not updated_product:
        raise ProductNotFoundError(
            f"Product with ID {product_id} not found for update."
        )

    return AdminProductDTO.model_validate(updated_product)


async def delete_product_by_id(session: AsyncSession, product_id: int) -> bool:
    """Service-level function to delete a product. Manages the transaction."""
    success = await crud.delete_product(session, product_id)
    return success
