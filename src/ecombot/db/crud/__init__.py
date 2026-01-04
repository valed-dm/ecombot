"""
CRUD (Create, Read, Update, Delete) operations for the e-commerce bot.

These functions encapsulate the database logic and are designed to be called
from within an active SQLAlchemy AsyncSession. They do not commit the session
themselves; the calling business logic (e.g., a bot handler) is responsible
for transaction management (commit/rollback).
"""

# Import all functions from submodules for backward compatibility
from .cart import add_item_to_cart
from .cart import clear_cart
from .cart import get_or_create_cart
from .cart import get_or_create_cart_lean
from .cart import set_cart_item_quantity
from .catalog import create_category
from .catalog import create_product
from .catalog import delete_product
from .catalog import get_categories
from .catalog import get_category_by_name
from .catalog import get_deleted_categories
from .catalog import get_deleted_products
from .catalog import get_product
from .catalog import get_products_by_category
from .catalog import restore_category
from .catalog import restore_product
from .catalog import soft_delete_category
from .catalog import update_product
from .orders import create_order_with_items
from .orders import get_order
from .orders import get_orders_by_status
from .orders import get_orders_by_user_pk
from .orders import restore_stock_for_order_items
from .orders import update_order_status
from .users import add_delivery_address
from .users import delete_delivery_address
from .users import get_or_create_user
from .users import get_user_addresses
from .users import set_default_address
from .users import update_user_profile


__all__ = [
    # Cart functions
    "add_item_to_cart",
    "clear_cart",
    "get_or_create_cart",
    "get_or_create_cart_lean",
    "set_cart_item_quantity",
    # Catalog functions
    "create_category",
    "create_product",
    "delete_product",
    "get_categories",
    "get_category_by_name",
    "get_deleted_categories",
    "get_deleted_products",
    "get_product",
    "get_products_by_category",
    "restore_category",
    "restore_product",
    "soft_delete_category",
    "update_product",
    # Order functions
    "create_order_with_items",
    "get_order",
    "get_orders_by_status",
    "get_orders_by_user_pk",
    "restore_stock_for_order_items",
    "update_order_status",
    # User functions
    "add_delivery_address",
    "delete_delivery_address",
    "get_or_create_user",
    "get_user_addresses",
    "set_default_address",
    "update_user_profile",
]
