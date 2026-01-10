from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.db.models import User
from ecombot.services import user_service
from ecombot.services.user_service import AddressNotFoundError


async def test_update_profile_details(mocker: MockerFixture, mock_session: AsyncMock):
    """Tests updating user profile."""
    user_id = 1
    update_data = {"phone": "555-5555"}
    mock_user = MagicMock(spec=User)

    mock_update_crud = mocker.patch(
        "ecombot.services.user_service.crud.update_user_profile",
        new_callable=AsyncMock,
        return_value=mock_user,
    )
    mocker.patch("ecombot.schemas.dto.UserProfileDTO.model_validate")

    await user_service.update_profile_details(
        session=mock_session, user_id=user_id, update_data=update_data
    )

    mock_update_crud.assert_awaited_once_with(mock_session, user_id, update_data)


async def test_delete_address_success(mocker: MockerFixture, mock_session: AsyncMock):
    """Tests successful address deletion."""
    user_id = 1
    address_id = 101

    mock_delete_crud = mocker.patch(
        "ecombot.services.user_service.crud.delete_delivery_address",
        new_callable=AsyncMock,
        return_value=True,
    )

    await user_service.delete_address(
        session=mock_session, user_id=user_id, address_id=address_id
    )

    mock_delete_crud.assert_awaited_once_with(mock_session, address_id, user_id)


async def test_delete_address_not_found(mocker: MockerFixture, mock_session: AsyncMock):
    """Tests error when address to delete is not found."""
    mocker.patch(
        "ecombot.services.user_service.crud.delete_delivery_address",
        new_callable=AsyncMock,
        return_value=False,
    )

    with pytest.raises(AddressNotFoundError):
        await user_service.delete_address(mock_session, 1, 101)


async def test_add_new_address(mocker: MockerFixture, mock_session: AsyncMock):
    """Test adding a new address."""
    mock_add_crud = mocker.patch(
        "ecombot.services.user_service.crud.add_delivery_address",
        new_callable=AsyncMock,
    )

    await user_service.add_new_address(
        mock_session, user_id=1, label="Home", address="123 St"
    )

    mock_add_crud.assert_awaited_once()
