"""Centralized management system combining messages, commands, and logging."""

from typing import Optional

from ..messages.admin_categories import AdminCategoriesMessageManager
from ..messages.admin_orders import AdminOrdersMessageManager
from ..messages.admin_products import AdminProductsMessageManager
from ..messages.cart import CartMessageManager
from ..messages.catalog import CatalogMessageManager
from ..messages.checkout import CheckoutMessageManager
from ..messages.common import CommonMessageManager
from ..messages.delivery import DeliveryMessageManager
from ..messages.keyboards import KeyboardMessageManager
from ..messages.orders import OrdersMessageManager
from ..messages.profile import ProfileMessageManager
from .commands import EcomBotCommandManager
from .logging import EcomBotLogManager
from .messages import Language


class CentralizedManager:
    """Main manager that provides access to all centralized systems."""

    def __init__(self, default_language: Language = Language.RU):
        self.default_language = default_language

        # Initialize all managers
        self.commands = EcomBotCommandManager(default_language)
        self.logs = EcomBotLogManager(default_language)
        self.messages = {
            "admin_categories": AdminCategoriesMessageManager(default_language),
            "admin_orders": AdminOrdersMessageManager(default_language),
            "admin_products": AdminProductsMessageManager(default_language),
            "common": CommonMessageManager(default_language),
            "catalog": CatalogMessageManager(default_language),
            "cart": CartMessageManager(default_language),
            "checkout": CheckoutMessageManager(default_language),
            "delivery": DeliveryMessageManager(default_language),
            "keyboards": KeyboardMessageManager(default_language),
            "orders": OrdersMessageManager(default_language),
            "profile": ProfileMessageManager(default_language),
        }

    def get_message(
        self, category: str, key: str, language: Optional[Language] = None, **kwargs
    ) -> str:
        """Get message from specific category."""
        if category in self.messages:
            return self.messages[category].get_message(key, language, **kwargs)
        return key

    def get_commands(self, role: str = "user", language: Optional[Language] = None):
        """Get commands for role and language."""
        return self.commands.get_commands(role, language)

    def log_info(self, key: str, language: Optional[Language] = None, **kwargs):
        """Log info message."""
        self.logs.log_info(key, language, **kwargs)

    def log_error(self, key: str, language: Optional[Language] = None, **kwargs):
        """Log error message."""
        self.logs.log_error(key, language, **kwargs)

    def log_warning(self, key: str, language: Optional[Language] = None, **kwargs):
        """Log warning message."""
        self.logs.log_warning(key, language, **kwargs)

    def log_debug(self, key: str, language: Optional[Language] = None, **kwargs):
        """Log debug message."""
        self.logs.log_debug(key, language, **kwargs)


# Global instance
central_manager = CentralizedManager()
