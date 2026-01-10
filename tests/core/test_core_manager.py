"""
Unit tests for the centralized manager.
"""

import pytest
from pytest_mock import MockerFixture

from ecombot.core.manager import CentralizedManager
from ecombot.core.messages import Language


@pytest.fixture
def mock_managers(mocker: MockerFixture):
    """Mocks all the sub-managers used by CentralizedManager."""
    return {
        "commands": mocker.patch("ecombot.core.manager.EcomBotCommandManager"),
        "logs": mocker.patch("ecombot.core.manager.EcomBotLogManager"),
        "admin_categories": mocker.patch(
            "ecombot.core.manager.AdminCategoriesMessageManager"
        ),
        "admin_orders": mocker.patch("ecombot.core.manager.AdminOrdersMessageManager"),
        "admin_products": mocker.patch(
            "ecombot.core.manager.AdminProductsMessageManager"
        ),
        "common": mocker.patch("ecombot.core.manager.CommonMessageManager"),
        "catalog": mocker.patch("ecombot.core.manager.CatalogMessageManager"),
        "cart": mocker.patch("ecombot.core.manager.CartMessageManager"),
        "checkout": mocker.patch("ecombot.core.manager.CheckoutMessageManager"),
        "keyboards": mocker.patch("ecombot.core.manager.KeyboardMessageManager"),
        "orders": mocker.patch("ecombot.core.manager.OrdersMessageManager"),
        "profile": mocker.patch("ecombot.core.manager.ProfileMessageManager"),
    }


def test_initialization(mock_managers):
    """Test that all sub-managers are initialized with the default language."""
    CentralizedManager(default_language=Language.ES)

    # Check commands and logs init
    mock_managers["commands"].assert_called_once_with(Language.ES)
    mock_managers["logs"].assert_called_once_with(Language.ES)

    # Check a few message managers
    mock_managers["common"].assert_called_once_with(Language.ES)
    mock_managers["cart"].assert_called_once_with(Language.ES)


def test_get_message_valid_category(mock_managers):
    """Test retrieving a message from a valid category."""
    manager = CentralizedManager()

    # Setup mock return
    mock_cart_instance = mock_managers["cart"].return_value
    mock_cart_instance.get_message.return_value = "Cart Message"

    result = manager.get_message("cart", "welcome", language=Language.FR, user="John")

    assert result == "Cart Message"
    mock_cart_instance.get_message.assert_called_once_with(
        "welcome", Language.FR, user="John"
    )


def test_get_message_invalid_category(mock_managers):
    """Test retrieving a message from a non-existent category."""
    manager = CentralizedManager()

    result = manager.get_message("unknown_category", "some_key")

    # Should return the key itself if category not found
    assert result == "some_key"


def test_get_commands(mock_managers):
    """Test retrieving commands."""
    manager = CentralizedManager()
    mock_cmd_instance = mock_managers["commands"].return_value
    mock_cmd_instance.get_commands.return_value = ["cmd1", "cmd2"]

    result = manager.get_commands(role="admin", language=Language.DE)

    assert result == ["cmd1", "cmd2"]
    mock_cmd_instance.get_commands.assert_called_once_with("admin", Language.DE)


def test_logging_methods(mock_managers):
    """Test logging delegation."""
    manager = CentralizedManager()
    mock_log_instance = mock_managers["logs"].return_value

    # Info
    manager.log_info("info_key", user_id=1)
    mock_log_instance.log_info.assert_called_once_with("info_key", None, user_id=1)

    # Error
    manager.log_error("error_key", Language.RU, error="Boom")
    mock_log_instance.log_error.assert_called_once_with(
        "error_key", Language.RU, error="Boom"
    )

    # Warning
    manager.log_warning("warn_key")
    mock_log_instance.log_warning.assert_called_once_with("warn_key", None)

    # Debug
    manager.log_debug("debug_key")
    mock_log_instance.log_debug.assert_called_once_with("debug_key", None)
