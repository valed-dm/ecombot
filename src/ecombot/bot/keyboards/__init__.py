"""
Keyboard package for the e-commerce bot.

This package organizes all inline and reply keyboards used throughout the bot
into logical modules for better maintainability and code organization.
"""

from .admin import *
from .cart import *
from .catalog import *
from .checkout import *
from .common import *
from .orders import *
from .profile import *

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