from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from sqlalchemy import Delete

from ecombot.db.crud import users as users_crud
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User


async def test_get_or_create_user_existing(mock_session: AsyncMock):
    """Test retrieving an existing user."""
    telegram_user = MagicMock(id=12345, username="testuser", full_name="Test User")
    existing_user = User(id=1, telegram_id=12345)

    # Mock database result
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = existing_user

    result = await users_crud.get_or_create_user(mock_session, telegram_user)

    assert result == existing_user
    mock_session.execute.assert_called_once()
    mock_session.add.assert_not_called()


async def test_get_or_create_user_new(mock_session: AsyncMock):
    """Test creating a new user when one does not exist."""
    telegram_user = MagicMock(id=12345, username="testuser", full_name="Test User")

    # Mock database result returning None
    mock_result = mock_session.execute.return_value
    mock_result.scalars.return_value.first.return_value = None

    result = await users_crud.get_or_create_user(mock_session, telegram_user)

    assert isinstance(result, User)
    assert result.telegram_id == 12345
    assert result.username == "testuser"
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result, attribute_names=["addresses"])


async def test_update_user_profile_success(mock_session: AsyncMock):
    """Test updating valid user profile fields."""
    user = User(id=1, phone="123", email="old@example.com")
    mock_session.get.return_value = user

    update_data = {"phone": "555-5555", "email": "new@example.com"}
    result = await users_crud.update_user_profile(mock_session, 1, update_data)

    assert result == user
    assert result.phone == "555-5555"
    assert result.email == "new@example.com"
    mock_session.flush.assert_awaited_once()


async def test_update_user_profile_invalid_fields(mock_session: AsyncMock):
    """Test that invalid fields are ignored during update."""
    user = User(id=1, username="original_user")
    mock_session.get.return_value = user

    # 'username' is not in allowed_fields (only phone, email, first_name)
    update_data = {"username": "new_user"}
    result = await users_crud.update_user_profile(mock_session, 1, update_data)

    assert result == user
    assert result.username == "original_user"  # Should not change
    mock_session.flush.assert_awaited_once()


async def test_get_user_addresses(mock_session: AsyncMock):
    """Test fetching all addresses for a user."""
    address = DeliveryAddress(id=1, user_id=1, full_address="123 St")
    mock_session.execute.return_value.scalars.return_value.all.return_value = [address]

    result = await users_crud.get_user_addresses(mock_session, 1)

    assert result == [address]
    mock_session.execute.assert_called_once()


async def test_add_delivery_address(mock_session: AsyncMock):
    """Test adding a new delivery address."""
    result = await users_crud.add_delivery_address(
        mock_session, user_id=1, label="Home", address="123 Main St"
    )

    assert isinstance(result, DeliveryAddress)
    assert result.user_id == 1
    assert result.address_label == "Home"
    assert result.full_address == "123 Main St"
    mock_session.add.assert_called_once_with(result)
    mock_session.flush.assert_awaited_once()


async def test_delete_delivery_address_success(mock_session: AsyncMock):
    """Test successful deletion of an address."""
    address = DeliveryAddress(id=10, user_id=1)
    mock_session.get.return_value = address
    mock_session.execute.return_value.rowcount = 1

    result = await users_crud.delete_delivery_address(
        mock_session, address_id=10, user_id=1
    )

    assert result is True
    # Verify delete statement execution
    mock_session.execute.assert_called()
    # Check that the last call was the delete execution
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Delete)
    mock_session.flush.assert_awaited_once()


async def test_delete_delivery_address_not_found(mock_session: AsyncMock):
    """Test deletion fails if address does not exist."""
    mock_session.get.return_value = None

    result = await users_crud.delete_delivery_address(
        mock_session, address_id=10, user_id=1
    )

    assert result is False
    mock_session.execute.assert_not_called()


async def test_delete_delivery_address_wrong_user(mock_session: AsyncMock):
    """Test deletion fails if address belongs to another user."""
    address = DeliveryAddress(id=10, user_id=2)  # Different user
    mock_session.get.return_value = address

    result = await users_crud.delete_delivery_address(
        mock_session, address_id=10, user_id=1
    )

    assert result is False
    mock_session.execute.assert_not_called()


async def test_set_default_address_success(mock_session: AsyncMock):
    """Test setting a default address."""
    user_id = 1
    address_id = 10
    address = DeliveryAddress(id=address_id, user_id=user_id, is_default=False)

    mock_session.get.return_value = address

    result = await users_crud.set_default_address(mock_session, user_id, address_id)

    assert result == address
    assert address.is_default is True

    # Verify that we executed the update to unset other defaults
    mock_session.execute.assert_called_once()
    mock_session.flush.assert_awaited_once()


async def test_set_default_address_not_found(mock_session: AsyncMock):
    """Test setting default fails if address not found or wrong user."""
    # Case 1: Address not found
    mock_session.get.return_value = None
    result = await users_crud.set_default_address(mock_session, 1, 10)
    assert result is None

    # Case 2: Wrong user
    address = DeliveryAddress(id=10, user_id=2)
    mock_session.get.return_value = address
    result = await users_crud.set_default_address(mock_session, 1, 10)
    assert result is None
    # Should still execute the unset update, but not flush the specific address update
    assert mock_session.execute.call_count == 2
