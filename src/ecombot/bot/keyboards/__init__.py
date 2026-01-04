"""Keyboard package for the e-commerce bot."""

from .admin import get_admin_order_details_keyboard
from .admin import get_admin_order_filters_keyboard
from .admin import get_admin_orders_list_keyboard
from .admin import get_admin_panel_keyboard
from .admin import get_edit_product_menu_keyboard
from .cart import get_cart_keyboard
from .catalog import get_catalog_categories_keyboard
from .catalog import get_catalog_products_keyboard
from .catalog import get_product_details_keyboard
from .checkout import get_checkout_confirmation_keyboard
from .checkout import get_fast_checkout_confirmation_keyboard
from .checkout import get_request_contact_keyboard
from .common import get_cancel_keyboard
from .common import get_delete_confirmation_keyboard
from .orders import get_order_details_keyboard
from .orders import get_orders_list_keyboard
from .profile import get_address_details_keyboard
from .profile import get_address_management_keyboard
from .profile import get_profile_keyboard


__all__ = [
    # Catalog keyboards
    "get_catalog_categories_keyboard",
    "get_catalog_products_keyboard",
    "get_product_details_keyboard",
    # Cart keyboards
    "get_cart_keyboard",
    # Admin keyboards
    "get_admin_panel_keyboard",
    "get_admin_orders_list_keyboard",
    "get_admin_order_filters_keyboard",
    "get_admin_order_details_keyboard",
    "get_edit_product_menu_keyboard",
    # Checkout keyboards
    "get_checkout_confirmation_keyboard",
    "get_fast_checkout_confirmation_keyboard",
    "get_request_contact_keyboard",
    # Profile keyboards
    "get_profile_keyboard",
    "get_address_management_keyboard",
    "get_address_details_keyboard",
    # Orders keyboards
    "get_orders_list_keyboard",
    "get_order_details_keyboard",
    # Common keyboards
    "get_delete_confirmation_keyboard",
    "get_cancel_keyboard",
]
