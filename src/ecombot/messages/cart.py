"""Cart messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class CartMessageManager(BaseMessageManager):
    """Message manager for cart-related messages."""
    
    def _load_messages(self) -> None:
        """Load cart messages for all supported languages."""
        
        # English messages
        en_messages = {
            # Success messages
            "success_added_to_cart": "✅ Product added to your cart!",
            "success_quantity_increased": "Quantity +1",
            "success_quantity_decreased": "Quantity -1",
            "success_item_removed": "Item removed",
            "success_cart_cleared": "🗑️ Cart cleared successfully!",
            
            # Cart display
            "cart_header": "🛒 Your Shopping Cart",
            "cart_empty_message": "🛒 <b>Your Shopping Cart</b>\n\nYour cart is currently empty.",
            "cart_total": "<b>Total: ${total:.2f}</b>",
            "cart_item_template": "• <b>{name}</b>\n  ${price:.2f} x {quantity} = ${subtotal:.2f}",
            
            # Actions
            "checkout_button": "✅ Checkout",
            "clear_cart_button": "🗑️ Clear Cart",
            "continue_shopping": "🛍️ Continue Shopping",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            
            # Error messages
            "error_user_not_identified": "Could not identify user.",
            "error_cart_item_not_found": "This item is no longer in your cart.",
            "error_add_to_cart_failed": "An error occurred while adding to cart.",
            "error_cart_update_failed": "Failed to update cart display.",
            "error_generic": "An error occurred.",
            "error_out_of_stock": "❌ Sorry, this product is out of stock.",
            "error_insufficient_stock": "❌ Not enough stock available. Only {available} items left.",
        }
        
        # Spanish messages
        es_messages = {
            # Success messages
            "success_added_to_cart": "✅ ¡Producto añadido a tu carrito!",
            "success_quantity_increased": "Cantidad +1",
            "success_quantity_decreased": "Cantidad -1",
            "success_item_removed": "Artículo eliminado",
            "success_cart_cleared": "🗑️ ¡Carrito vaciado exitosamente!",
            
            # Cart display
            "cart_header": "🛒 Tu Carrito de Compras",
            "cart_empty_message": "🛒 <b>Tu Carrito de Compras</b>\n\nTu carrito está actualmente vacío.",
            "cart_total": "<b>Total: ${total:.2f}</b>",
            "cart_item_template": "• <b>{name}</b>\n  ${price:.2f} x {quantity} = ${subtotal:.2f}",
            
            # Actions
            "checkout_button": "✅ Finalizar Compra",
            "clear_cart_button": "🗑️ Vaciar Carrito",
            "continue_shopping": "🛍️ Seguir Comprando",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            
            # Error messages
            "error_user_not_identified": "No se pudo identificar al usuario.",
            "error_cart_item_not_found": "Este artículo ya no está en tu carrito.",
            "error_add_to_cart_failed": "Ocurrió un error al añadir al carrito.",
            "error_cart_update_failed": "Error al actualizar la visualización del carrito.",
            "error_generic": "Ocurrió un error.",
            "error_out_of_stock": "❌ Lo siento, este producto está agotado.",
            "error_insufficient_stock": "❌ Stock insuficiente. Solo quedan {available} artículos.",
        }
        
        # Russian messages
        ru_messages = {
            # Success messages
            "success_added_to_cart": "✅ Товар добавлен в корзину!",
            "success_quantity_increased": "Количество +1",
            "success_quantity_decreased": "Количество -1",
            "success_item_removed": "Товар удален",
            "success_cart_cleared": "🗑️ Корзина успешно очищена!",
            
            # Cart display
            "cart_header": "🛒 Ваша Корзина",
            "cart_empty_message": "🛒 <b>Ваша Корзина</b>\n\nВаша корзина пуста.",
            "cart_total": "<b>Итого: ${total:.2f}</b>",
            "cart_item_template": "• <b>{name}</b>\n  ${price:.2f} x {quantity} = ${subtotal:.2f}",
            
            # Actions
            "checkout_button": "✅ Оформить Заказ",
            "clear_cart_button": "🗑️ Очистить Корзину",
            "continue_shopping": "🛍️ Продолжить Покупки",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            
            # Error messages
            "error_user_not_identified": "Не удалось идентифицировать пользователя.",
            "error_cart_item_not_found": "Этого товара больше нет в вашей корзине.",
            "error_add_to_cart_failed": "Произошла ошибка при добавлении в корзину.",
            "error_cart_update_failed": "Не удалось обновить отображение корзины.",
            "error_generic": "Произошла ошибка.",
            "error_out_of_stock": "❌ Извините, этот товар закончился.",
            "error_insufficient_stock": "❌ Недостаточно товара на складе. Осталось только {available} шт.",
        }
        
        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }