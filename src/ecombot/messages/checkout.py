"""Checkout messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class CheckoutMessageManager(BaseMessageManager):
    """Message manager for checkout-related messages."""
    
    def _load_messages(self) -> None:
        """Load checkout messages for all supported languages."""
        
        # English messages
        en_messages = {
            # Error messages
            "error_empty_cart": "Your cart is empty.",
            "error_address_not_found": (
                "Error: Could not find your default address. "
                "Please try again or update your profile."
            ),
            "error_unexpected": "An unexpected error occurred. Please contact support.",
            "error_empty_phone": "Please enter a valid phone number (cannot be empty).",
            "error_empty_address": (
                "Please enter a valid shipping address (cannot be empty)."
            ),
            
            # Success messages
            "success_order_placed": (
                "✅ <b>Thank you! Your order #{order_number} has been placed!</b>"
            ),
            "success_order_placed_slow": (
                "✅ <b>Thank you! Your order has been placed successfully!</b>\n\n"
                "<b>Order Number:</b> <code>{order_number}</code>\n"
                "You can view its status in /orders."
            ),
            
            # Progress messages
            "progress_placing_order": "Placing your order, please wait...",
            "progress_saving_details": "Placing your order and saving your details...",
            
            # Cancellation message
            "checkout_cancelled": "Checkout cancelled.",
            
            # Slow path prompts
            "slow_path_start": (
                "To complete your order, we need to set up your {missing_info}.\n\n"
                "Let's start with your full name (as it should appear on the package)."
            ),
            "slow_path_phone": "Thank you. Now, please share your phone number.",
            "slow_path_address": "Great. Finally, what is the full shipping address?",
            
            # Fast path messages
            "fast_path_confirm": (
                "Ready to place your order?\n\n"
                "<b>Delivery to:</b> {address}\n"
                "<b>Phone:</b> {phone}\n\n"
                "Confirm to proceed with checkout."
            ),
            
            # Buttons
            "confirm_order": "✅ Confirm Order",
            "cancel_checkout": "❌ Cancel",
            "back_to_cart": "🛒 Back to Cart",
        }
        
        # Spanish messages
        es_messages = {
            # Error messages
            "error_empty_cart": "Tu carrito está vacío.",
            "error_address_not_found": (
                "Error: No se pudo encontrar tu dirección predeterminada. "
                "Por favor, inténtalo de nuevo o actualiza tu perfil."
            ),
            "error_unexpected": (
                "Ocurrió un error inesperado. Por favor, contacta al soporte."
            ),
            "error_empty_phone": (
                "Por favor, ingresa un número de teléfono válido (no puede estar vacío)."
            ),
            "error_empty_address": (
                "Por favor, ingresa una dirección de envío válida (no puede estar vacía)."
            ),
            
            # Success messages
            "success_order_placed": (
                "✅ <b>¡Gracias! ¡Tu pedido #{order_number} ha sido realizado!</b>"
            ),
            "success_order_placed_slow": (
                "✅ <b>¡Gracias! ¡Tu pedido ha sido realizado exitosamente!</b>\n\n"
                "<b>Número de Pedido:</b> <code>{order_number}</code>\n"
                "Puedes ver su estado en /orders."
            ),
            
            # Progress messages
            "progress_placing_order": "Realizando tu pedido, por favor espera...",
            "progress_saving_details": (
                "Realizando tu pedido y guardando tus detalles..."
            ),
            
            # Cancellation message
            "checkout_cancelled": "Checkout cancelado.",
            
            # Slow path prompts
            "slow_path_start": (
                "Para completar tu pedido, necesitamos configurar tu {missing_info}.\n\n"
                "Comencemos con tu nombre completo "
                "(como debe aparecer en el paquete)."
            ),
            "slow_path_phone": "Gracias. Ahora, por favor comparte tu número de teléfono.",
            "slow_path_address": (
                "Perfecto. Finalmente, ¿cuál es la dirección de envío completa?"
            ),
            
            # Fast path messages
            "fast_path_confirm": (
                "¿Listo para realizar tu pedido?\n\n"
                "<b>Entrega a:</b> {address}\n"
                "<b>Teléfono:</b> {phone}\n\n"
                "Confirma para proceder con el checkout."
            ),
            
            # Buttons
            "confirm_order": "✅ Confirmar Pedido",
            "cancel_checkout": "❌ Cancelar",
            "back_to_cart": "🛒 Volver al Carrito",
        }
        
        # Russian messages
        ru_messages = {
            # Error messages
            "error_empty_cart": "Ваша корзина пуста.",
            "error_address_not_found": (
                "Ошибка: Не удалось найти ваш адрес по умолчанию. "
                "Пожалуйста, попробуйте снова или обновите ваш профиль."
            ),
            "error_unexpected": (
                "Произошла неожиданная ошибка. Пожалуйста, обратитесь в поддержку."
            ),
            "error_empty_phone": (
                "Пожалуйста, введите действительный номер телефона (не может быть пустым)."
            ),
            "error_empty_address": (
                "Пожалуйста, введите действительный адрес доставки (не может быть пустым)."
            ),
            
            # Success messages
            "success_order_placed": (
                "✅ <b>Спасибо! Ваш заказ #{order_number} оформлен!</b>"
            ),
            "success_order_placed_slow": (
                "✅ <b>Спасибо! Ваш заказ успешно оформлен!</b>\n\n"
                "<b>Номер Заказа:</b> <code>{order_number}</code>\n"
                "Вы можете посмотреть его статус в /orders."
            ),
            
            # Progress messages
            "progress_placing_order": "Оформляем ваш заказ, пожалуйста подождите...",
            "progress_saving_details": (
                "Оформляем ваш заказ и сохраняем ваши данные..."
            ),
            
            # Cancellation message
            "checkout_cancelled": "Оформление заказа отменено.",
            
            # Slow path prompts
            "slow_path_start": (
                "Для завершения заказа нам нужно настроить ваши {missing_info}.\n\n"
                "Начнем с вашего полного имени "
                "(как оно должно появиться на посылке)."
            ),
            "slow_path_phone": "Спасибо. Теперь, пожалуйста, поделитесь номером телефона.",
            "slow_path_address": (
                "Отлично. И наконец, какой полный адрес доставки?"
            ),
            
            # Fast path messages
            "fast_path_confirm": (
                "Готовы оформить заказ?\n\n"
                "<b>Доставка по адресу:</b> {address}\n"
                "<b>Телефон:</b> {phone}\n\n"
                "Подтвердите для продолжения оформления."
            ),
            
            # Buttons
            "confirm_order": "✅ Подтвердить Заказ",
            "cancel_checkout": "❌ Отменить",
            "back_to_cart": "🛒 Назад в Корзину",
        }
        
        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }