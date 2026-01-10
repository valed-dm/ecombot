"""
Unit tests for the 'Add Category' admin handler.

This module verifies the Finite State Machine (FSM) flow for adding new product
categories, ensuring that:
- The conversation starts correctly and handles message editing failures.
- Category names are validated for length and emptiness.
- Descriptions are validated and can be skipped.
- The catalog service is called with the correct parameters.
- Exceptions like `CategoryAlreadyExistsError` are handled gracefully with user
  feedback.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.exceptions import TelegramBadRequest
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.handlers.admin.categories import add
from ecombot.bot.handlers.admin.categories.states import AddCategory
from ecombot.services.catalog_service import CategoryAlreadyExistsError


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.categories.add.manager")


async def test_add_category_start(
    mock_manager: MagicMock,
):
    """Test the start of the add category flow."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_manager.get_message.return_value = "Enter name"

    await add.add_category_start(query, callback_data, state, callback_message)

    # Should edit the message with the prompt
    callback_message.edit_text.assert_awaited_once()
    # Should set the FSM state
    state.set_state.assert_awaited_once_with(AddCategory.name)
    query.answer.assert_awaited_once()


async def test_add_category_start_bad_request(
    mock_manager: MagicMock,
):
    """Test fallback to answer() if edit_text fails (e.g., message too old)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    # Simulate TelegramBadRequest when trying to edit
    callback_message.edit_text.side_effect = TelegramBadRequest(
        method="editMessageText", message="Bad Request: message is not modified"
    )

    await add.add_category_start(query, callback_data, state, callback_message)

    # Should fall back to sending a new message
    callback_message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(AddCategory.name)
    query.answer.assert_awaited_once()


async def test_add_category_name_valid(
    mock_manager: MagicMock,
):
    """Test providing a valid category name."""
    message = AsyncMock()
    message.text = "New Category"
    state = AsyncMock()

    await add.add_category_name(message, state)

    # Should save name to state data
    state.update_data.assert_awaited_once_with(name="New Category")
    # Should ask for description
    message.answer.assert_awaited_once()
    # Should advance state
    state.set_state.assert_awaited_once_with(AddCategory.description)


async def test_add_category_name_empty(
    mock_manager: MagicMock,
):
    """Test providing an empty or whitespace-only name."""
    message = AsyncMock()
    message.text = "   "
    state = AsyncMock()

    await add.add_category_name(message, state)

    state.update_data.assert_not_awaited()
    message.answer.assert_awaited_once()  # Should send error message
    state.set_state.assert_not_awaited()


async def test_add_category_name_too_long(
    mock_manager: MagicMock,
):
    """Test providing a name that exceeds the length limit."""
    message = AsyncMock()
    message.text = "a" * 256  # Limit is 255
    state = AsyncMock()

    await add.add_category_name(message, state)

    state.update_data.assert_not_awaited()
    message.answer.assert_awaited_once()  # Should send error message
    state.set_state.assert_not_awaited()


async def test_add_category_description_valid(
    mock_manager: MagicMock,
    mocker: MockerFixture,
    mock_session: AsyncMock,
):
    """Test providing a valid description and successfully creating the category."""
    message = AsyncMock()
    message.text = "Description"
    state = AsyncMock()
    state.get_data.return_value = {"name": "CatName"}

    mock_service = mocker.patch(
        "ecombot.bot.handlers.admin.categories.add.catalog_service.add_new_category",
        new_callable=AsyncMock,
    )
    mock_service.return_value = MagicMock(name="CatName")

    await add.add_category_description(message, state, mock_session)

    mock_service.assert_awaited_once_with(
        session=mock_session, name="CatName", description="Description"
    )
    message.answer.assert_awaited_once()  # Success message
    state.clear.assert_awaited_once()


async def test_add_category_description_skip(
    mock_manager: MagicMock,
    mocker: MockerFixture,
    mock_session: AsyncMock,
):
    """Test skipping the description."""
    message = AsyncMock()
    message.text = "/skip"
    state = AsyncMock()
    state.get_data.return_value = {"name": "CatName"}

    mock_service = mocker.patch(
        "ecombot.bot.handlers.admin.categories.add.catalog_service.add_new_category",
        new_callable=AsyncMock,
    )
    mock_service.return_value = MagicMock(name="CatName")

    await add.add_category_description(message, state, mock_session)

    # Should call service with description=None
    mock_service.assert_awaited_once_with(
        session=mock_session, name="CatName", description=None
    )
    state.clear.assert_awaited_once()


async def test_add_category_description_too_long(
    mock_manager: MagicMock,
    mocker: MockerFixture,
    mock_session: AsyncMock,
):
    """Test providing a description that is too long."""
    message = AsyncMock()
    message.text = "a" * 1001  # Limit is 1000
    state = AsyncMock()
    state.get_data.return_value = {"name": "CatName"}

    mock_service = mocker.patch(
        "ecombot.bot.handlers.admin.categories.add.catalog_service.add_new_category",
        new_callable=AsyncMock,
    )

    await add.add_category_description(message, state, mock_session)

    mock_service.assert_not_awaited()
    message.answer.assert_awaited_once()  # Error message
    state.clear.assert_not_awaited()


async def test_add_category_already_exists(
    mock_manager: MagicMock,
    mocker: MockerFixture,
    mock_session: AsyncMock,
):
    """Test handling of CategoryAlreadyExistsError."""
    message = AsyncMock()
    message.text = "Desc"
    state = AsyncMock()
    state.get_data.return_value = {"name": "ExistingCat"}

    mock_service = mocker.patch(
        "ecombot.bot.handlers.admin.categories.add.catalog_service.add_new_category",
        new_callable=AsyncMock,
    )
    mock_service.side_effect = CategoryAlreadyExistsError("Exists")

    await add.add_category_description(message, state, mock_session)

    message.answer.assert_awaited_once()  # Specific error message
    state.clear.assert_awaited_once()
