"""Message managers for different application modules."""

from .admin_categories import AdminCategoriesMessageManager
from .admin_orders import AdminOrdersMessageManager
from .admin_products import AdminProductsMessageManager
from .cart import CartMessageManager
from .catalog import CatalogMessageManager
from .checkout import CheckoutMessageManager
from .common import CommonMessageManager
from .keyboards import KeyboardMessageManager
from .orders import OrdersMessageManager
from .profile import ProfileMessageManager


__all__ = [
    "AdminCategoriesMessageManager",
    "AdminOrdersMessageManager",
    "AdminProductsMessageManager",
    "CommonMessageManager",
    "CatalogMessageManager",
    "CartMessageManager",
    "CheckoutMessageManager",
    "KeyboardMessageManager",
    "OrdersMessageManager",
    "ProfileMessageManager",
]
