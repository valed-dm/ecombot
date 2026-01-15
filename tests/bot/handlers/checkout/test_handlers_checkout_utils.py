"""
Unit tests for checkout utilities.

This module verifies:
- Retrieval of default address.
- Determination of missing user info.
- Generation of confirmation texts for fast and slow paths.
"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.checkout import utils
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.schemas.dto import CartDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.checkout.utils.manager")

    # Mock get_message to return a predictable string or format
    def get_message_side_effect(section, key, **kwargs):
        if key == "currency_symbol":
            return "$"
        if key == "fast_path_confirm":
            return f"Confirm: {kwargs.get('address')}, {kwargs.get('phone')}"
        if key == "slow_path_confirm":
            return (
                f"Confirm Slow: {kwargs.get('name')}, {kwargs.get('phone')}, "
                f"{kwargs.get('address')}"
            )
        if key == "total_price_line":
            # Format to 2 decimal places to match test assertions
            # (e.g., 50.0 -> "50.00")
            total = kwargs.get("total")
            return (
                f"Total: ${total:.2f}"
                if isinstance(total, (int, float))
                else f"Total: {total}"
            )
        if key.startswith("missing_"):
            return f"[{key}]"
        return f"[{key}]"

    manager.get_message.side_effect = get_message_side_effect
    return manager


def test_get_default_address_found():
    """Test finding the default address."""
    addr1 = MagicMock(spec=DeliveryAddress, is_default=False)
    addr2 = MagicMock(spec=DeliveryAddress, is_default=True)
    user = MagicMock(spec=User, addresses=[addr1, addr2])

    result = utils.get_default_address(user)
    assert result == addr2


def test_get_default_address_none_found():
    """Test when no address is marked default."""
    addr1 = MagicMock(spec=DeliveryAddress, is_default=False)
    user = MagicMock(spec=User, addresses=[addr1])

    result = utils.get_default_address(user)
    assert result is None


def test_get_default_address_no_addresses():
    """Test when user has no addresses."""
    user = MagicMock(spec=User, addresses=[])
    result = utils.get_default_address(user)
    assert result is None


def test_determine_missing_info_none(mock_manager):
    """Test when all info is present."""
    user = MagicMock(spec=User, phone="123")
    address = MagicMock(spec=DeliveryAddress)

    result = utils.determine_missing_info(user, address)
    assert result == []


def test_determine_missing_info_phone(mock_manager):
    """Test when phone is missing."""
    user = MagicMock(spec=User, phone=None)
    address = MagicMock(spec=DeliveryAddress)

    result = utils.determine_missing_info(user, address)
    assert "[missing_phone]" in result
    assert "[missing_address]" not in result


def test_determine_missing_info_address(mock_manager):
    """Test when address is missing."""
    user = MagicMock(spec=User, phone="123")

    result = utils.determine_missing_info(user, None)
    assert "[missing_address]" in result
    assert "[missing_phone]" not in result


def test_determine_missing_info_both(mock_manager):
    """Test when both are missing."""
    user = MagicMock(spec=User, phone=None)

    result = utils.determine_missing_info(user, None)
    assert "[missing_phone]" in result
    assert "[missing_address]" in result


def test_generate_fast_path_confirmation_text(mock_manager):
    """Test text generation for fast path."""
    user = MagicMock(spec=User, phone="555-1234")
    address = MagicMock(spec=DeliveryAddress, full_address="123 Main St")
    cart = MagicMock(spec=CartDTO, total_price=100.50)

    text = utils.generate_fast_path_confirmation_text(user, address, cart)

    assert "123 Main St" in text
    assert "555-1234" in text
    assert "100.50" in text
    assert "$" in text  # Currency symbol


def test_generate_slow_path_confirmation_text(mock_manager):
    """Test text generation for slow path."""
    user_data = {"name": "John Doe", "phone": "555-9876", "address": "456 Elm St"}
    cart = MagicMock(spec=CartDTO, total_price=50.00)

    text = utils.generate_slow_path_confirmation_text(user_data, cart)

    assert "Confirm Slow: John Doe, 555-9876, 456 Elm St" in text
    assert "50.00" in text
    assert "$" in text
