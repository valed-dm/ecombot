from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.db.models import Cart
from ecombot.services import cart_service
from ecombot.services.cart_service import ProductNotFoundError


async def test_get_user_cart(mocker: MockerFixture, mock_session: AsyncMock):
    """Test retrieving the user's cart."""
    user_id = 123
    mock_cart = MagicMock(spec=Cart)

    mock_get_crud = mocker.patch(
        "ecombot.services.cart_service.crud.get_or_create_cart",
        new_callable=AsyncMock,
        return_value=mock_cart,
    )
    mock_validate = mocker.patch("ecombot.schemas.dto.CartDTO.model_validate")

    await cart_service.get_user_cart(mock_session, user_id)

    mock_get_crud.assert_awaited_once_with(mock_session, user_id)
    mock_validate.assert_called_once_with(mock_cart)


async def test_add_product_to_cart_success(
    mocker: MockerFixture, mock_session: AsyncMock
):
    """Test adding a product to the cart."""
    user_id = 123
    product_id = 1

    mock_product = MagicMock()
    mock_product.id = product_id

    mock_cart = MagicMock(spec=Cart)

    mocker.patch(
        "ecombot.services.cart_service.crud.get_product",
        new_callable=AsyncMock,
        return_value=mock_product,
    )
    mocker.patch(
        "ecombot.services.cart_service.crud.get_or_create_cart_lean",
        new_callable=AsyncMock,
        return_value=mock_cart,
    )
    mock_add_item = mocker.patch(
        "ecombot.services.cart_service.crud.add_item_to_cart", new_callable=AsyncMock
    )
    mocker.patch(
        "ecombot.services.cart_service.crud.get_or_create_cart",
        new_callable=AsyncMock,
        return_value=MagicMock(spec=Cart),
    )
    mocker.patch("ecombot.schemas.dto.CartDTO.model_validate")

    await cart_service.add_product_to_cart(
        session=mock_session, user_id=user_id, product_id=product_id, quantity=1
    )

    mock_add_item.assert_awaited_once()


async def test_add_product_to_cart_not_found(
    mocker: MockerFixture, mock_session: AsyncMock
):
    """Test error when product does not exist."""
    mocker.patch(
        "ecombot.services.cart_service.crud.get_product",
        new_callable=AsyncMock,
        return_value=None,
    )

    with pytest.raises(ProductNotFoundError):
        await cart_service.add_product_to_cart(mock_session, 123, 999)


async def test_alter_item_quantity_success(
    mocker: MockerFixture, mock_session: AsyncMock
):
    """Test altering item quantity."""
    user_id = 123
    item_id = 10

    # Mock cart with item
    mock_item = MagicMock()
    mock_item.id = item_id
    mock_item.quantity = 1
    mock_cart = MagicMock(spec=Cart, items=[mock_item])

    mocker.patch(
        "ecombot.services.cart_service.crud.get_or_create_cart",
        new_callable=AsyncMock,
        return_value=mock_cart,
    )
    mock_set_qty = mocker.patch(
        "ecombot.services.cart_service.crud.set_cart_item_quantity",
        new_callable=AsyncMock,
    )
    mocker.patch("ecombot.schemas.dto.CartDTO.model_validate")

    await cart_service.alter_item_quantity(mock_session, user_id, item_id, "increase")

    mock_set_qty.assert_awaited_once_with(mock_session, item_id, 2)
