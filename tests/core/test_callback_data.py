"""
Unit tests for callback data factories.

This module verifies that the CallbackData definitions correctly pack and unpack
data, ensuring that prefixes and field types are handled as expected.
"""

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import AdminNavCallbackFactory
from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.callback_data import ProfileCallbackFactory


def test_admin_callback_factory():
    """Test AdminCallbackFactory packing and unpacking."""
    # Test with item_id
    cb = AdminCallbackFactory(action="test_action", item_id=123)
    packed = cb.pack()
    assert packed == "admin:test_action:123"

    unpacked = AdminCallbackFactory.unpack(packed)
    assert unpacked.action == "test_action"
    assert unpacked.item_id == 123

    # Test without item_id (optional)
    cb_none = AdminCallbackFactory(action="test_action")
    packed_none = cb_none.pack()
    # We verify unpacking to be sure about None handling
    unpacked_none = AdminCallbackFactory.unpack(packed_none)
    assert unpacked_none.action == "test_action"
    assert unpacked_none.item_id is None


def test_admin_nav_callback_factory():
    """Test AdminNavCallbackFactory packing and unpacking."""
    cb = AdminNavCallbackFactory(
        action="navigate", target_message_id=100, category_id=5
    )
    packed = cb.pack()
    assert packed == "admin_nav:navigate:100:5"

    unpacked = AdminNavCallbackFactory.unpack(packed)
    assert unpacked.action == "navigate"
    assert unpacked.target_message_id == 100
    assert unpacked.category_id == 5


def test_catalog_callback_factory():
    """Test CatalogCallbackFactory packing and unpacking."""
    cb = CatalogCallbackFactory(action="view", item_id=10)
    packed = cb.pack()
    assert packed == "catalog:view:10"

    unpacked = CatalogCallbackFactory.unpack(packed)
    assert unpacked.action == "view"
    assert unpacked.item_id == 10


def test_cart_callback_factory():
    """Test CartCallbackFactory packing and unpacking."""
    cb = CartCallbackFactory(action="add", item_id=99)
    packed = cb.pack()
    assert packed == "cart:add:99"

    unpacked = CartCallbackFactory.unpack(packed)
    assert unpacked.action == "add"
    assert unpacked.item_id == 99


def test_order_callback_factory():
    """Test OrderCallbackFactory packing and unpacking."""
    # With ID
    cb = OrderCallbackFactory(action="details", item_id=55)
    packed = cb.pack()
    assert packed == "order:details:55"

    unpacked = OrderCallbackFactory.unpack(packed)
    assert unpacked.action == "details"
    assert unpacked.item_id == 55

    # Without ID
    cb_none = OrderCallbackFactory(action="list")
    packed_none = cb_none.pack()
    unpacked_none = OrderCallbackFactory.unpack(packed_none)
    assert unpacked_none.action == "list"
    assert unpacked_none.item_id is None


def test_edit_product_callback_factory():
    """Test EditProductCallbackFactory packing and unpacking."""
    cb = EditProductCallbackFactory(action="price", product_id=10)
    packed = cb.pack()
    assert packed == "edit_prod:price:10"

    unpacked = EditProductCallbackFactory.unpack(packed)
    assert unpacked.action == "price"
    assert unpacked.product_id == 10


def test_confirmation_callback_factory():
    """Test ConfirmationCallbackFactory packing and unpacking."""
    # Test True
    cb_true = ConfirmationCallbackFactory(action="delete", item_id=1, confirm=True)
    packed_true = cb_true.pack()
    # aiogram converts bool to string "1"
    assert packed_true == "confirm:delete:1:1"

    unpacked_true = ConfirmationCallbackFactory.unpack(packed_true)
    assert unpacked_true.confirm is True

    # Test False
    cb_false = ConfirmationCallbackFactory(action="delete", item_id=1, confirm=False)
    packed_false = cb_false.pack()
    assert packed_false == "confirm:delete:1:0"

    unpacked_false = ConfirmationCallbackFactory.unpack(packed_false)
    assert unpacked_false.confirm is False


def test_checkout_callback_factory():
    """Test CheckoutCallbackFactory packing and unpacking."""
    cb = CheckoutCallbackFactory(action="confirm")
    packed = cb.pack()
    assert packed == "checkout:confirm"

    unpacked = CheckoutCallbackFactory.unpack(packed)
    assert unpacked.action == "confirm"


def test_profile_callback_factory():
    """Test ProfileCallbackFactory packing and unpacking."""
    # With ID
    cb = ProfileCallbackFactory(action="edit_addr", address_id=5)
    packed = cb.pack()
    assert packed == "profile:edit_addr:5"

    unpacked = ProfileCallbackFactory.unpack(packed)
    assert unpacked.action == "edit_addr"
    assert unpacked.address_id == 5

    # Without ID
    cb_none = ProfileCallbackFactory(action="view_main")
    packed_none = cb_none.pack()
    unpacked_none = ProfileCallbackFactory.unpack(packed_none)
    assert unpacked_none.action == "view_main"
    assert unpacked_none.address_id is None
