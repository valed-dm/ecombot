from unittest.mock import AsyncMock

import pytest
from sqlalchemy import Delete

from ecombot.db.crud import cart as cart_crud
from ecombot.db.models import Cart
from ecombot.db.models import CartItem
from ecombot.db.models import Product


async def test_get_or_create_cart_existing(mock_session: AsyncMock):
    """Test retrieving an existing cart with eager loading."""
    user_id = 123
    existing_cart = Cart(id=1, user_id=user_id)

    # Mock the database result
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = existing_cart

    result = await cart_crud.get_or_create_cart(mock_session, user_id)

    assert result == existing_cart
    mock_session.execute.assert_called_once()
    # Should not try to create a new one
    mock_session.add.assert_not_called()


async def test_get_or_create_cart_creates_new(mock_session: AsyncMock):
    """Test creating a new cart when one does not exist."""
    user_id = 123

    # Mock the database result to return None
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = None

    result = await cart_crud.get_or_create_cart(mock_session, user_id)

    assert isinstance(result, Cart)
    assert result.user_id == user_id
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result, attribute_names=["items"])


async def test_get_or_create_cart_lean_existing(mock_session: AsyncMock):
    """Test retrieving a lean cart (no eager loads)."""
    user_id = 123
    existing_cart = Cart(id=1, user_id=user_id)

    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = existing_cart

    result = await cart_crud.get_or_create_cart_lean(mock_session, user_id)

    assert result == existing_cart
    mock_session.execute.assert_called_once()
    mock_session.refresh.assert_not_awaited()


async def test_add_item_to_cart_new_item(mock_session: AsyncMock):
    """Test adding a new product to the cart."""
    cart = Cart(id=1, user_id=123)
    product = Product(id=10, name="Test Product", price=100)
    quantity = 2

    # Mock query to return no existing item
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = None

    result = await cart_crud.add_item_to_cart(mock_session, cart, product, quantity)

    assert isinstance(result, CartItem)
    assert result.cart_id == cart.id
    assert result.product_id == product.id
    assert result.quantity == quantity
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()


async def test_add_item_to_cart_existing_item(mock_session: AsyncMock):
    """Test updating quantity for an existing product in the cart."""
    cart = Cart(id=1, user_id=123)
    product = Product(id=10, name="Test Product", price=100)
    existing_item = CartItem(id=5, cart_id=1, product_id=10, quantity=1)

    # Mock query to return existing item
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = existing_item

    result = await cart_crud.add_item_to_cart(mock_session, cart, product, quantity=2)

    assert result == existing_item
    assert result.quantity == 3  # 1 existing + 2 added
    mock_session.add.assert_not_called()  # Should not add new object
    mock_session.flush.assert_awaited_once()


async def test_add_item_to_cart_invalid_quantity(mock_session: AsyncMock):
    """Test that adding zero or negative quantity raises ValueError."""
    cart = Cart(id=1)
    product = Product(id=10)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        await cart_crud.add_item_to_cart(mock_session, cart, product, quantity=0)


async def test_set_cart_item_quantity_update(mock_session: AsyncMock):
    """Test updating a cart item to a specific valid quantity."""
    item_id = 5
    existing_item = CartItem(id=item_id, quantity=1)
    mock_session.get.return_value = existing_item

    result = await cart_crud.set_cart_item_quantity(mock_session, item_id, 5)

    assert result == existing_item
    assert result.quantity == 5
    mock_session.flush.assert_awaited_once()
    mock_session.execute.assert_not_called()  # No delete should happen


async def test_set_cart_item_quantity_remove(mock_session: AsyncMock):
    """Test that setting quantity to 0 deletes the item."""
    item_id = 5
    existing_item = CartItem(id=item_id, quantity=1)
    mock_session.get.return_value = existing_item

    result = await cart_crud.set_cart_item_quantity(mock_session, item_id, 0)

    assert result is None
    # Verify delete was executed
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Delete)
    mock_session.flush.assert_awaited_once()


async def test_set_cart_item_quantity_not_found(mock_session: AsyncMock):
    """Test setting quantity for a non-existent item returns None."""
    mock_session.get.return_value = None

    result = await cart_crud.set_cart_item_quantity(mock_session, 999, 5)

    assert result is None
    mock_session.flush.assert_not_awaited()


async def test_set_cart_item_quantity_limits(mock_session: AsyncMock):
    """Test validation limits for quantity."""
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        await cart_crud.set_cart_item_quantity(mock_session, 1, -1)

    with pytest.raises(ValueError, match="Quantity cannot exceed 100"):
        await cart_crud.set_cart_item_quantity(mock_session, 1, 101)


async def test_clear_cart(mock_session: AsyncMock):
    """Test clearing all items from a cart."""
    cart = Cart(id=1, items=[CartItem(id=1), CartItem(id=2)])

    await cart_crud.clear_cart(mock_session, cart)

    # Verify delete statement execution
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Delete)

    # Verify local object state is updated
    assert cart.items == []
    mock_session.flush.assert_awaited_once()
