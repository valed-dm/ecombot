"""Centralized logging system with internationalization support."""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional

from loguru import logger

from .messages import Language


class BaseLogManager(ABC):
    """Abstract base class for logging with i18n support."""

    def __init__(self, default_language: Language = Language.EN):
        self.default_language = default_language
        self._log_messages: Dict[Language, Dict[str, str]] = {}
        self._load_log_messages()

    @abstractmethod
    def _load_log_messages(self) -> None:
        """Load log messages for all supported languages."""
        pass

    def get_log_message(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> str:
        """Get localized log message with optional formatting."""
        lang = language or self.default_language

        # Fallback to default language if key not found
        if lang not in self._log_messages or key not in self._log_messages[lang]:
            lang = self.default_language

        # Fallback to key if still not found
        if lang not in self._log_messages or key not in self._log_messages[lang]:
            return key

        message = self._log_messages[lang][key]

        # Format message with provided kwargs
        if kwargs:
            try:
                return message.format(**kwargs)
            except (KeyError, ValueError):
                return message

        return message

    def log_info(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> None:
        """Log info message."""
        message = self.get_log_message(key, language, **kwargs)
        logger.info(message)

    def log_warning(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> None:
        """Log warning message."""
        message = self.get_log_message(key, language, **kwargs)
        logger.warning(message)

    def log_error(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> None:
        """Log error message."""
        message = self.get_log_message(key, language, **kwargs)
        logger.error(message)

    def log_debug(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> None:
        """Log debug message."""
        message = self.get_log_message(key, language, **kwargs)
        logger.debug(message)


class EcomBotLogManager(BaseLogManager):
    """Concrete implementation for EcomBot logging."""

    def _load_log_messages(self) -> None:
        """Load log messages for all supported languages."""

        # English log messages
        en_messages = {
            # Database operations
            "db_user_created": "User created: {user_id} ({first_name})",
            "db_user_updated": "User updated: {user_id}",
            "db_product_created": "Product created: {product_name} (ID: {product_id})",
            "db_product_deleted": "Product deleted: {product_name} (ID: {product_id})",
            "db_category_created": (
                "Category created: {category_name} (ID: {category_id})"
            ),
            "db_category_deleted": (
                "Category deleted: {category_name} (ID: {category_id})"
            ),
            "db_order_created": "Order created: {order_number} for user {user_id}",
            "db_order_status_changed": (
                "Order {order_number} status changed to {status}"
            ),
            # Authentication & Authorization
            "admin_access_granted": "Admin access granted to user {user_id}",
            "admin_access_denied": "Admin access denied to user {user_id}",
            "user_middleware_processed": "User middleware processed for {user_id}",
            # Business logic
            "cart_item_added": (
                "Item added to cart: {product_name} x{quantity} for user {user_id}"
            ),
            "cart_cleared": "Cart cleared for user {user_id}",
            "checkout_started": "Checkout started for user {user_id}",
            "checkout_completed": "Checkout completed: {order_number}",
            "stock_updated": (
                "Stock updated for product {product_id}: {old_stock} -> {new_stock}"
            ),
            # Errors
            "validation_error": "Validation error: {error_details}",
            "database_error": "Database error: {error_details}",
            "api_error": "API error: {error_details}",
            "unexpected_error": "Unexpected error: {error_details}",
        }

        # Spanish log messages
        es_messages = {
            # Database operations
            "db_user_created": "Usuario creado: {user_id} ({first_name})",
            "db_user_updated": "Usuario actualizado: {user_id}",
            "db_product_created": "Producto creado: {product_name} (ID: {product_id})",
            "db_product_deleted": (
                "Producto eliminado: {product_name} (ID: {product_id})"
            ),
            "db_category_created": (
                "Categoría creada: {category_name} (ID: {category_id})"
            ),
            "db_category_deleted": (
                "Categoría eliminada: {category_name} (ID: {category_id})"
            ),
            "db_order_created": "Pedido creado: {order_number} para usuario {user_id}",
            "db_order_status_changed": (
                "Estado del pedido {order_number} cambiado a {status}"
            ),
            # Authentication & Authorization
            "admin_access_granted": (
                "Acceso de administrador concedido al usuario {user_id}"
            ),
            "admin_access_denied": (
                "Acceso de administrador denegado al usuario {user_id}"
            ),
            "user_middleware_processed": (
                "Middleware de usuario procesado para {user_id}"
            ),
            # Business logic
            "cart_item_added": (
                "Artículo añadido al carrito: {product_name} x{quantity} "
                "para usuario {user_id}"
            ),
            "cart_cleared": "Carrito vaciado para usuario {user_id}",
            "checkout_started": "Checkout iniciado para usuario {user_id}",
            "checkout_completed": "Checkout completado: {order_number}",
            "stock_updated": (
                "Stock actualizado para producto {product_id}: "
                "{old_stock} -> {new_stock}"
            ),
            # Errors
            "validation_error": "Error de validación: {error_details}",
            "database_error": "Error de base de datos: {error_details}",
            "api_error": "Error de API: {error_details}",
            "unexpected_error": "Error inesperado: {error_details}",
        }

        self._log_messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
        }
