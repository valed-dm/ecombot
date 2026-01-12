from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from ecombot.db.crud import orders as orders_crud
from ecombot.db.models import CartItem
from ecombot.db.models import Order
from ecombot.db.models import OrderItem
from ecombot.db.models import Product
from ecombot.schemas.enums import OrderStatus


async def test_create_order_with_items_success(mock_session: AsyncMock):
    """
    Test successful order creation.
    Verifies that:
    1. Order object is created.
    2. Stock is deducted from products.
    3. OrderItems are created.
    """
    user_id = 1
    items = [
        MagicMock(spec=CartItem, product_id=10, quantity=2),
        MagicMock(spec=CartItem, product_id=11, quantity=1),
    ]

    # Mock products that will be fetched from DB
    product1 = Product(id=10, name="P1", price=100, stock=10)
    product2 = Product(id=11, name="P2", price=50, stock=5)

    # session.get is called for each product in the loop
    mock_session.get.side_effect = [product1, product2]

    result = await orders_crud.create_order_with_items(
        mock_session,
        user_id,
        "John Doe",
        "555-1234",
        "123 Main St",
        "Courier",
        items,
    )

    assert isinstance(result, Order)
    assert result.user_id == user_id
    assert result.contact_name == "John Doe"
    # Order number format is JJJ-HHMMSS-XXXX (e.g., 001-120000-abcd)
    assert len(result.order_number.split("-")) == 3

    # Verify stock deduction
    assert product1.stock == 8  # 10 - 2
    assert product2.stock == 4  # 5 - 1

    # Verify session.add calls: 1 for Order + 2 for OrderItems
    assert mock_session.add.call_count == 3
    mock_session.flush.assert_awaited()


async def test_create_order_insufficient_stock(mock_session: AsyncMock):
    """Test that InsufficientStockError is raised when stock is low."""
    items = [MagicMock(spec=CartItem, product_id=10, quantity=5)]
    product = Product(id=10, name="P1", stock=2)  # Only 2 available

    mock_session.get.return_value = product

    with pytest.raises(orders_crud.InsufficientStockError):
        await orders_crud.create_order_with_items(
            mock_session, 1, "Name", "Phone", "Addr", "Method", items
        )

    # Stock should remain unchanged
    assert product.stock == 2


async def test_create_order_product_not_found(mock_session: AsyncMock):
    """Test error when a product in the cart does not exist in DB."""
    items = [MagicMock(spec=CartItem, product_id=10, quantity=1)]
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Product with ID 10 not found"):
        await orders_crud.create_order_with_items(
            mock_session, 1, "Name", "Phone", "Addr", "Method", items
        )


async def test_get_order(mock_session: AsyncMock):
    """
    Test fetching a single order.
    Verifies that the manual loading of products (including deleted ones) occurs.
    """
    order = Order(id=1, items=[OrderItem(product_id=10)])
    product = Product(id=10, name="Test Product")

    # 1. Mock result for get_order query
    mock_order_result = MagicMock()
    mock_order_result.scalars.return_value.first.return_value = order

    # 2. Mock result for the product query inside the loop
    mock_product_result = MagicMock()
    mock_product_result.scalars.return_value.first.return_value = product

    mock_session.execute.side_effect = [mock_order_result, mock_product_result]

    result = await orders_crud.get_order(mock_session, 1)

    assert result == order
    assert result.items[0].product == product
    assert mock_session.execute.call_count == 2


async def test_get_orders_by_user_pk(mock_session: AsyncMock):
    """Test fetching orders for a specific user."""
    order = Order(id=1, items=[])
    mock_session.execute.return_value.scalars.return_value.all.return_value = [order]

    result = await orders_crud.get_orders_by_user_pk(mock_session, 1)

    assert result == [order]
    mock_session.execute.assert_called_once()


async def test_get_orders_by_status(mock_session: AsyncMock):
    """Test fetching orders filtered by status."""
    order = Order(id=1, status=OrderStatus.PAID, items=[])
    mock_session.execute.return_value.scalars.return_value.all.return_value = [order]

    result = await orders_crud.get_orders_by_status(mock_session, OrderStatus.PAID)

    assert result == [order]
    mock_session.execute.assert_called_once()


async def test_update_order_status(mock_session: AsyncMock):
    """Test updating the status of an order."""
    # 1. Mock the update statement execution (returning ID 1)
    mock_update_result = MagicMock()
    mock_update_result.scalar_one_or_none.return_value = 1

    # 2. Mock the subsequent get_order call
    # We return an order with no items to avoid mocking the inner product loop
    mock_order = Order(id=1, status=OrderStatus.PAID, items=[])
    mock_get_result = MagicMock()
    mock_get_result.scalars.return_value.first.return_value = mock_order

    mock_session.execute.side_effect = [mock_update_result, mock_get_result]

    result = await orders_crud.update_order_status(mock_session, 1, OrderStatus.PAID)

    assert result == mock_order
    assert result.status == OrderStatus.PAID
    mock_session.flush.assert_awaited_once()


async def test_restore_stock_for_order_items(mock_session: AsyncMock):
    """Test restoring stock for cancelled order items."""
    items = [OrderItem(product_id=10, quantity=2)]
    product = Product(id=10, stock=5)

    mock_session.get.return_value = product

    await orders_crud.restore_stock_for_order_items(mock_session, items)

    assert product.stock == 7  # 5 + 2
    mock_session.flush.assert_awaited_once()


async def test_restore_stock_product_not_found(mock_session: AsyncMock):
    """
    Test restoring stock when the product no longer exists.
    Should log a warning but not crash.
    """
    items = [OrderItem(product_id=10, quantity=2)]

    # Simulate product not found (e.g. hard deleted)
    mock_session.get.return_value = None

    await orders_crud.restore_stock_for_order_items(mock_session, items)

    # Should just flush without error
    mock_session.flush.assert_awaited_once()
