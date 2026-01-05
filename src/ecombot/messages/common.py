"""Common messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class CommonMessageManager(BaseMessageManager):
    """Message manager for common application messages."""

    def _load_messages(self) -> None:
        """Load common messages for all supported languages."""

        # English messages
        en_messages = {
            # Navigation
            "back_to_main": "⬅️ Back to Main Menu",
            "back_to_admin": "⬅️ Back to Admin Panel",
            "cancel_operation": "❌ Cancel",
            # Common actions
            "loading": "⏳ Loading...",
            "processing": "⚙️ Processing...",
            "success": "✅ Success!",
            "error": "❌ Error occurred",
            "not_found": "❌ Not found",
            "access_denied": "🚫 Access denied",
            # Confirmations
            "confirm_action": "Are you sure you want to proceed?",
            "yes": "✅ Yes",
            "no": "❌ No",
            # Generic messages
            "welcome": "👋 Welcome to EcomBot!",
            "goodbye": "👋 Goodbye! Thank you for using EcomBot.",
            "invalid_input": "❌ Invalid input. Please try again.",
            "operation_cancelled": "❌ Operation cancelled.",
        }

        # Spanish messages
        es_messages = {
            # Navigation
            "back_to_main": "⬅️ Volver al Menú Principal",
            "back_to_admin": "⬅️ Volver al Panel de Administración",
            "cancel_operation": "❌ Cancelar",
            # Common actions
            "loading": "⏳ Cargando...",
            "processing": "⚙️ Procesando...",
            "success": "✅ ¡Éxito!",
            "error": "❌ Ocurrió un error",
            "not_found": "❌ No encontrado",
            "access_denied": "🚫 Acceso denegado",
            # Confirmations
            "confirm_action": "¿Estás seguro de que quieres continuar?",
            "yes": "✅ Sí",
            "no": "❌ No",
            # Generic messages
            "welcome": "👋 ¡Bienvenido a EcomBot!",
            "goodbye": "👋 ¡Adiós! Gracias por usar EcomBot.",
            "invalid_input": "❌ Entrada inválida. Por favor, inténtalo de nuevo.",
            "operation_cancelled": "❌ Operación cancelada.",
        }

        # Russian messages
        ru_messages = {
            # Navigation
            "back_to_main": "⬅️ Назад в Главное Меню",
            "back_to_admin": "⬅️ Назад в Панель Администратора",
            "cancel_operation": "❌ Отменить",
            # Common actions
            "loading": "⏳ Загрузка...",
            "processing": "⚙️ Обработка...",
            "success": "✅ Успешно!",
            "error": "❌ Произошла ошибка",
            "not_found": "❌ Не найдено",
            "access_denied": "🚫 Доступ запрещен",
            # Confirmations
            "confirm_action": "Вы уверены, что хотите продолжить?",
            "yes": "✅ Да",
            "no": "❌ Нет",
            # Generic messages
            "welcome": "👋 Добро пожаловать в EcomBot!",
            "goodbye": "👋 До свидания! Спасибо за использование EcomBot.",
            "invalid_input": "❌ Неверный ввод. Пожалуйста, попробуйте снова.",
            "operation_cancelled": "❌ Операция отменена.",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
