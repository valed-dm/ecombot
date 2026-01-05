"""Centralized command management system."""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from aiogram.types import BotCommand

from .messages import Language


class BaseCommandManager(ABC):
    """Abstract base class for command management with i18n support."""

    def __init__(self, default_language: Language = Language.EN):
        self.default_language = default_language
        self._commands: Dict[Language, Dict[str, BotCommand]] = {}
        self._load_commands()

    @abstractmethod
    def _load_commands(self) -> None:
        """Load commands for all supported languages."""
        pass

    def get_commands(
        self, role: str = "user", language: Optional[Language] = None
    ) -> List[BotCommand]:
        """Get commands for specific role and language."""
        lang = language or self.default_language

        # Fallback to default language if not found
        if lang not in self._commands:
            lang = self.default_language

        if lang not in self._commands:
            return []

        commands = []
        for cmd_key, command in self._commands[lang].items():
            if self._is_command_for_role(cmd_key, role):
                commands.append(command)

        return commands

    def _is_command_for_role(self, command_key: str, role: str) -> bool:
        """Check if command is available for the given role."""
        admin_commands = {"admin", "cancel"}

        if role == "admin":
            return True
        elif role == "user":
            return command_key not in admin_commands

        return False

    def add_command(
        self, key: str, command: str, description: str, language: Language
    ) -> None:
        """Add or update a command for a specific language."""
        if language not in self._commands:
            self._commands[language] = {}

        self._commands[language][key] = BotCommand(
            command=command, description=description
        )


class EcomBotCommandManager(BaseCommandManager):
    """Concrete implementation for EcomBot commands."""

    def _load_commands(self) -> None:
        """Load all commands for supported languages."""
        # English commands
        en_commands = {
            "start": BotCommand(command="start", description="🛍️ Browse catalog"),
            "cart": BotCommand(command="cart", description="🛒 View shopping cart"),
            "orders": BotCommand(command="orders", description="📦 Order history"),
            "profile": BotCommand(command="profile", description="👤 Manage profile"),
            "admin": BotCommand(command="admin", description="⚙️ Admin panel"),
            "cancel": BotCommand(command="cancel", description="❌ Cancel operation"),
        }

        # Spanish commands
        es_commands = {
            "start": BotCommand(command="start", description="🛍️ Explorar catálogo"),
            "cart": BotCommand(command="cart", description="🛒 Ver carrito"),
            "orders": BotCommand(
                command="orders", description="📦 Historial de pedidos"
            ),
            "profile": BotCommand(command="profile", description="👤 Gestionar perfil"),
            "admin": BotCommand(
                command="admin", description="⚙️ Panel de administración"
            ),
            "cancel": BotCommand(command="cancel", description="❌ Cancelar operación"),
        }

        # Russian commands
        ru_commands = {
            "start": BotCommand(command="start", description="🛍️ Просмотр каталога"),
            "cart": BotCommand(command="cart", description="🛒 Корзина покупок"),
            "orders": BotCommand(command="orders", description="📦 История заказов"),
            "profile": BotCommand(
                command="profile", description="👤 Управление профилем"
            ),
            "admin": BotCommand(command="admin", description="⚙️ Панель администратора"),
            "cancel": BotCommand(command="cancel", description="❌ Отменить операцию"),
        }

        self._commands = {
            Language.EN: en_commands,
            Language.ES: es_commands,
            Language.RU: ru_commands,
        }
