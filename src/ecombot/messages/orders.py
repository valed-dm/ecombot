"""Orders messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class OrdersMessageManager(BaseMessageManager):
    """Message manager for orders-related messages."""

    def _load_messages(self) -> None:
        """Load orders messages for all supported languages."""

        # English messages
        en_messages = {
            # Header messages
            "order_history_header": "<b>Your Order History</b>\n\n",
            "order_details_header": "<b>Details for Order #{order_id}</b>\n",
            "order_items_header": "<b>Items:</b>\n",
            # Status and content messages
            "no_orders_message": "You have not placed any orders yet.",
            "order_status_updated": "Order status has been updated to: {status}",
            # Order display templates
            "order_list_item": (
                "📦 <b>Order #{order_number}</b> - <i>{status}</i>\n"
                "Placed on: {date}\n"
                "Total: ${total:.2f}\n\n"
            ),
            "order_item_template": (
                "  - <b>{name}</b>\n"
                "    <code>{quantity} x ${price:.2f} = ${total:.2f}</code>\n"
            ),
            # Actions
            "view_details": "📋 View Details",
            "back_to_orders": "⬅️ Back to Orders",
            # Error messages
            "error_order_not_found": "Could not find this order.",
            "error_loading_orders": "Error loading your orders. Please try again.",
            # Date format (technical, not user-facing)
            "date_format": "%Y-%m-%d %H:%M",
        }

        # Spanish messages
        es_messages = {
            # Header messages
            "order_history_header": "<b>Tu Historial de Pedidos</b>\n\n",
            "order_details_header": "<b>Detalles del Pedido #{order_id}</b>\n",
            "order_items_header": "<b>Artículos:</b>\n",
            # Status and content messages
            "no_orders_message": "Aún no has realizado ningún pedido.",
            "order_status_updated": (
                "El estado del pedido se ha actualizado a: {status}"
            ),
            # Order display templates
            "order_list_item": (
                "📦 <b>Pedido #{order_number}</b> - <i>{status}</i>\n"
                "Realizado el: {date}\n"
                "Total: €{total:.2f}\n\n"
            ),
            "order_item_template": (
                "  - <b>{name}</b>\n"
                "    <code>{quantity} x €{price:.2f} = €{total:.2f}</code>\n"
            ),
            # Actions
            "view_details": "📋 Ver Detalles",
            "back_to_orders": "⬅️ Volver a Pedidos",
            # Error messages
            "error_order_not_found": "No se pudo encontrar este pedido.",
            "error_loading_orders": (
                "Error al cargar tus pedidos. Por favor, inténtalo de nuevo."
            ),
            # Date format (technical, not user-facing)
            "date_format": "%Y-%m-%d %H:%M",
        }

        # Russian messages
        ru_messages = {
            # Header messages
            "order_history_header": "<b>История Ваших Заказов</b>\n\n",
            "order_details_header": "<b>Детали Заказа #{order_id}</b>\n",
            "order_items_header": "<b>Товары:</b>\n",
            # Status and content messages
            "no_orders_message": "Вы еще не сделали ни одного заказа.",
            "order_status_updated": "Статус заказа обновлен на: {status}",
            # Order display templates
            "order_list_item": (
                "📦 <b>Заказ #{order_number}</b> - <i>{status}</i>\n"
                "Размещен: {date}\n"
                "Итого: ₽{total:.2f}\n\n"
            ),
            "order_item_template": (
                "  - <b>{name}</b>\n"
                "    <code>{quantity} x ₽{price:.2f} = ₽{total:.2f}</code>\n"
            ),
            # Actions
            "view_details": "📋 Посмотреть Детали",
            "back_to_orders": "⬅️ Назад к Заказам",
            # Error messages
            "error_order_not_found": "Не удалось найти этот заказ.",
            "error_loading_orders": (
                "Ошибка загрузки ваших заказов. Пожалуйста, попробуйте снова."
            ),
            # Date format (technical, not user-facing)
            "date_format": "%Y-%m-%d %H:%M",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
