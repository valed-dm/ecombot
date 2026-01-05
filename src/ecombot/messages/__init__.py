"""Message managers for different application modules."""

from .admin_orders import AdminOrdersMessageManager
from .cart import CartMessageManager
from .catalog import CatalogMessageManager
from .checkout import CheckoutMessageManager
from .common import CommonMessageManager
from .keyboards import KeyboardMessageManager
from .orders import OrdersMessageManager
from .profile import ProfileMessageManager


__all__ = [
    "AdminOrdersMessageManager",
    "CommonMessageManager",
    "CatalogMessageManager",
    "CartMessageManager",
    "CheckoutMessageManager",
    "KeyboardMessageManager",
    "OrdersMessageManager",
    "ProfileMessageManager",
]
