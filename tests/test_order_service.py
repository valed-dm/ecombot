from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.db.models import Cart
from ecombot.db.models import CartItem
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import Order
from ecombot.db.models import User
from ecombot.services import order_service
from ecombot.services.order_service import OrderPlacementError


async def test_place_order_success(mocker: MockerFixture, mock_session: AsyncMock):
    """Tests the successful placement of an order from a cart."""
    mock_user = MagicMock(spec=User, id=1, telegram_id=123)
    mock_address = MagicMock(spec=DeliveryAddress, id=1, full_address="123 Main St")
    mock_cart = MagicMock(spec=Cart, items=[MagicMock(spec=CartItem)])
    mock_order = MagicMock(spec=Order, id=99)

    mocker.patch(
        "ecombot.services.order_service.crud.get_or_create_cart",
        new_callable=AsyncMock,
        return_value=mock_cart,
    )
    mock_create = mocker.patch(
        "ecombot.services.order_service.crud.create_order_with_items",
        new_callable=AsyncMock,
        return_value=mock_order,
    )
    mock_clear = mocker.patch(
        "ecombot.services.order_service.crud.clear_cart", new_callable=AsyncMock
    )
    mocker.patch(
        "ecombot.services.order_service.crud.get_order",
        new_callable=AsyncMock,
        return_value=mock_order,
    )
    mocker.patch("ecombot.schemas.dto.OrderDTO.model_validate")

    await order_service.place_order(
        session=mock_session, db_user=mock_user, delivery_address=mock_address
    )

    mock_create.assert_awaited_once()
    mock_clear.assert_awaited_once()


async def test_place_order_insufficient_stock(
    mocker: MockerFixture, mock_session: AsyncMock
):
    """Tests that place_order handles stock errors correctly."""
    mock_user = MagicMock(spec=User, id=1, telegram_id=123)
    mock_address = MagicMock(spec=DeliveryAddress)
    mock_cart = MagicMock(spec=Cart, items=[MagicMock(spec=CartItem)])

    mocker.patch(
        "ecombot.services.order_service.crud.get_or_create_cart",
        new_callable=AsyncMock,
        return_value=mock_cart,
    )
    # Simulate CRUD raising the specific stock error (or ValueError which service
    # catches)
    mocker.patch(
        "ecombot.services.order_service.crud.create_order_with_items",
        new_callable=AsyncMock,
        side_effect=ValueError("Not enough stock"),
    )

    with pytest.raises(OrderPlacementError, match="Not enough stock"):
        await order_service.place_order(
            session=mock_session, db_user=mock_user, delivery_address=mock_address
        )


async def test_list_user_orders(mocker: MockerFixture, mock_session: AsyncMock):
    """Test listing user orders."""
    user_id = 123
    mock_orders = [MagicMock(spec=Order), MagicMock(spec=Order)]

    mock_get_orders = mocker.patch(
        "ecombot.services.order_service.crud.get_orders_by_user_pk",
        new_callable=AsyncMock,
        return_value=mock_orders,
    )
    mocker.patch("ecombot.schemas.dto.OrderDTO.model_validate")

    result = await order_service.list_user_orders(mock_session, user_id)

    mock_get_orders.assert_awaited_once_with(mock_session, user_id)
    assert len(result) == 2
