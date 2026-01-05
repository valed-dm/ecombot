"""Abstract base classes for centralized message management."""

from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional


class Language(Enum):
    """Supported languages."""

    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    RU = "ru"


class MessageCategory(Enum):
    """Message categories for organization."""

    COMMON = "common"
    CATALOG = "catalog"
    CART = "cart"
    ORDERS = "orders"
    PROFILE = "profile"
    ADMIN = "admin"
    CHECKOUT = "checkout"
    ERRORS = "errors"


class BaseMessageManager(ABC):
    """Abstract base class for message management with i18n support."""

    def __init__(self, default_language: Language = Language.EN):
        self.default_language = default_language
        self._messages: Dict[Language, Dict[str, str]] = {}
        self._load_messages()

    @abstractmethod
    def _load_messages(self) -> None:
        """Load messages for all supported languages."""
        pass

    def get_message(
        self, key: str, language: Optional[Language] = None, **kwargs: Any
    ) -> str:
        """Get localized message with optional formatting."""
        lang = language or self.default_language

        # Fallback to default language if key not found
        if lang not in self._messages or key not in self._messages[lang]:
            lang = self.default_language

        # Fallback to key if still not found
        if lang not in self._messages or key not in self._messages[lang]:
            return key

        message = self._messages[lang][key]

        # Format message with provided kwargs
        if kwargs:
            try:
                return message.format(**kwargs)
            except (KeyError, ValueError):
                return message

        return message

    def add_message(self, key: str, message: str, language: Language) -> None:
        """Add or update a message for a specific language."""
        if language not in self._messages:
            self._messages[language] = {}
        self._messages[language][key] = message

    def get_supported_languages(self) -> list[Language]:
        """Get list of supported languages."""
        return list(self._messages.keys())
