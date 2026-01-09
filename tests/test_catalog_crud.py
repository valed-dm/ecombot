from decimal import Decimal
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from ecombot.db.crud import catalog as catalog_crud
from ecombot.db.models import Category
from ecombot.db.models import Product


async def test_create_category(mock_session: AsyncMock):
    """Test creating a new category."""
    name = "Electronics"
    description = "Gadgets"

    result = await catalog_crud.create_category(mock_session, name, description)

    assert isinstance(result, Category)
    assert result.name == name
    assert result.description == description
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()


async def test_get_categories(mock_session: AsyncMock):
    """Test fetching all active top-level categories."""
    mock_cat = Category(id=1, name="Test")
    mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_cat]

    result = await catalog_crud.get_categories(mock_session)

    assert result == [mock_cat]
    mock_session.execute.assert_called_once()


async def test_get_category_by_name(mock_session: AsyncMock):
    """Test fetching a category by name."""
    mock_cat = Category(id=1, name="Test")
    mock_session.execute.return_value.scalars.return_value.first.return_value = mock_cat

    result = await catalog_crud.get_category_by_name(mock_session, "Test")

    assert result == mock_cat


async def test_create_product_success(mock_session: AsyncMock):
    """Test creating a product with valid data."""
    category = Category(id=1, name="Cat")
    mock_session.get.return_value = category

    result = await catalog_crud.create_product(
        mock_session, "Prod", "Desc", Decimal("10.0"), 5, 1
    )

    assert isinstance(result, Product)
    assert result.price == Decimal("10.0")
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()


async def test_create_product_invalid_price(mock_session: AsyncMock):
    """Test that creating a product with negative price raises ValueError."""
    with pytest.raises(ValueError, match="Price must be positive"):
        await catalog_crud.create_product(
            mock_session, "Prod", "Desc", Decimal("-10.0"), 5, 1
        )


async def test_create_product_invalid_stock(mock_session: AsyncMock):
    """Test that creating a product with negative stock raises ValueError."""
    with pytest.raises(ValueError, match="Stock must be non-negative"):
        await catalog_crud.create_product(
            mock_session, "Prod", "Desc", Decimal("10.0"), -1, 1
        )


async def test_create_product_category_not_found(mock_session: AsyncMock):
    """Test that creating a product for a non-existent category raises ValueError."""
    mock_session.get.return_value = None
    with pytest.raises(ValueError, match="Category with ID 1 does not exist"):
        await catalog_crud.create_product(
            mock_session, "Prod", "Desc", Decimal("10.0"), 5, 1
        )


async def test_get_product(mock_session: AsyncMock):
    """Test fetching a single product."""
    mock_prod = Product(id=1)
    mock_session.execute.return_value.scalars.return_value.first.return_value = (
        mock_prod
    )
    result = await catalog_crud.get_product(mock_session, 1)
    assert result == mock_prod


async def test_get_products_by_category(mock_session: AsyncMock):
    """Test fetching products for a specific category."""
    mock_prod = Product(id=1, name="P1")
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        mock_prod
    ]

    result = await catalog_crud.get_products_by_category(mock_session, 1)

    assert result == [mock_prod]


async def test_update_product_success(mock_session: AsyncMock):
    """Test updating a product."""
    mock_product = Product(id=1, name="Updated")

    # 1. Mock the update statement execution (returning ID 1)
    mock_update_result = MagicMock()
    mock_update_result.scalar_one_or_none.return_value = 1

    # 2. Mock the subsequent get_product call (returning the object)
    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = mock_product

    mock_session.execute.side_effect = [mock_update_result, mock_select_result]

    result = await catalog_crud.update_product(mock_session, 1, {"name": "Updated"})

    assert result == mock_product
    assert mock_session.execute.call_count == 2


async def test_soft_delete_product(mock_session: AsyncMock):
    """
    Test soft deleting a product.
    Verifies stock restoration logic and cart cleanup.
    """
    product = Product(id=1, stock=10, deleted_at=None)
    mock_session.get.return_value = product

    # Sequence of expected execute calls:
    # 1. Select sum of quantity from OrderItems (to calculate sold stock)
    # 2. Delete from CartItems
    # 3. Update Product (set deleted_at and restore stock)

    mock_sold_result = MagicMock()
    mock_sold_result.scalar.return_value = 5  # 5 items sold

    mock_delete_cart_result = MagicMock()

    mock_update_prod_result = MagicMock()
    mock_update_prod_result.rowcount = 1

    mock_session.execute.side_effect = [
        mock_sold_result,
        mock_delete_cart_result,
        mock_update_prod_result,
    ]

    result = await catalog_crud.soft_delete_product(mock_session, 1)

    assert result is True
    assert mock_session.execute.call_count == 3
    mock_session.flush.assert_awaited_once()


async def test_soft_delete_category(mock_session: AsyncMock):
    """
    Test soft deleting a category.
    Verifies cascading soft delete to products and subcategories.
    """
    category = Category(id=1, deleted_at=None)
    mock_session.get.return_value = category

    # Sequence of expected execute calls:
    # 1. Select all product IDs in category
    # 2. (Loop) Select sum of quantity for product
    # 3. (Loop) Update product (soft delete + stock restore)
    # 4. Delete from CartItems (bulk)
    # 5. Update subcategories (soft delete)
    # 6. Update category (soft delete)

    mock_products_result = MagicMock()
    mock_products_result.fetchall.return_value = [(10,)]  # One product with ID 10

    mock_sold_result = MagicMock()
    mock_sold_result.scalar.return_value = 2

    mock_update_prod_result = MagicMock()

    mock_delete_cart_result = MagicMock()
    mock_update_sub_result = MagicMock()

    mock_update_cat_result = MagicMock()
    mock_update_cat_result.rowcount = 1

    mock_session.execute.side_effect = [
        mock_products_result,
        mock_sold_result,
        mock_update_prod_result,
        mock_delete_cart_result,
        mock_update_sub_result,
        mock_update_cat_result,
    ]

    result = await catalog_crud.soft_delete_category(mock_session, 1)

    assert result is True
    assert mock_session.execute.call_count == 6
    mock_session.flush.assert_awaited_once()


async def test_restore_category(mock_session: AsyncMock):
    """
    Test restoring a soft-deleted category.
    Verifies cascading restore to products and subcategories.
    """
    category = Category(id=1, deleted_at="2023-01-01")

    # Sequence of expected calls:
    # 1. session.get(Category)
    # 2. Update category (restore)
    # 3. Select soft-deleted product IDs
    # 4. (Loop) Select sum of quantity (sold)
    # 5. (Loop) session.get(Product)
    # 6. (Loop) Update product (restore + stock adjust)
    # 7. Update subcategories (restore)

    mock_restore_cat_result = MagicMock()
    mock_restore_cat_result.rowcount = 1

    mock_products_result = MagicMock()
    mock_products_result.fetchall.return_value = [(10,)]

    mock_sold_result = MagicMock()
    mock_sold_result.scalar.return_value = 2

    mock_product = Product(id=10, stock=5)
    mock_restore_prod_result = MagicMock()
    mock_restore_sub_result = MagicMock()

    # session.get is called twice: once for category, once for product inside loop
    mock_session.get.side_effect = [category, mock_product]

    mock_session.execute.side_effect = [
        mock_restore_cat_result,
        mock_products_result,
        mock_sold_result,
        mock_restore_prod_result,
        mock_restore_sub_result,
    ]

    result = await catalog_crud.restore_category(mock_session, 1)

    assert result is True
    assert mock_session.execute.call_count == 5
