"""Admin orders messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class AdminOrdersMessageManager(BaseMessageManager):
    """Message manager for admin order management messages."""

    def _load_messages(self) -> None:
        """Load admin orders messages for all supported languages."""

        # English messages
        en_messages = {
            # Error messages
            "error_query_data_none": "Query data cannot be None",
            "error_order_not_found": "Could not find this order.",
            "error_invalid_order_id": "Invalid order ID format.",
            "error_status_update_failed": (
                "An error occurred while updating the status."
            ),
            # Success messages
            "success_status_updated": "Order status updated to {status}",
            # Progress messages
            "progress_fetching_orders": "Fetching {status} orders, please wait...",
            # UI text
            "select_status_prompt": "Please select a status to view orders:",
            "orders_list_header": "<b>Orders - {status} ({count})</b>\n\n",
            "no_orders_found": "No orders found with this status.",
            "text_truncated_suffix": "\n\n[Truncated due to length]",
            # Order details template
            "order_details_header": "<b>Order Details: {order_number}</b>\n\n",
            "order_status_field": "<b>Status:</b> <i>{status}</i>\n",
            "order_date_field": "<b>Placed on:</b> {date}\n\n",
            "customer_info_header": (
                "<b>Customer:</b> {name}\n"
                "<b>Phone:</b> <code>{phone}</code>\n"
                "<b>Address:</b> <code>{address}</code>\n\n"
            ),
            "items_header": "<b>Items:</b>\n",
            "deleted_product_suffix": " ⚠️ <i>(Deleted - Not Charged)</i>",
            "item_template": (
                "  - <b>{name}</b>{status}\n"
                "    <code>{quantity} x ${price:.2f} = ${total:.2f}</code>\n"
            ),
            "active_items_total": "<b>Active Items Total: ${total:.2f}</b>\n",
            "deleted_items_total": "<s>Deleted Items: ${total:.2f}</s>\n",
            "final_total": "<b>Final Total: ${total:.2f}</b>\n\n",
            "deleted_items_notice": (
                "⚠️ <i>Deleted products are not charged. "
                "Customer pays only for active items.</i>"
            ),
            "order_total": "<b>Total: ${total:.2f}</b>",
            "not_available": "N/A",
            # Technical constants
            "max_message_length": "4096",
            "truncate_threshold": "4090",
        }

        # Spanish messages
        es_messages = {
            # Error messages
            "error_query_data_none": "Los datos de consulta no pueden ser nulos",
            "error_order_not_found": "No se pudo encontrar este pedido.",
            "error_invalid_order_id": "Formato de ID de pedido inválido.",
            "error_status_update_failed": ("Ocurrió un error al actualizar el estado."),
            # Success messages
            "success_status_updated": "Estado del pedido actualizado a {status}",
            # Progress messages
            "progress_fetching_orders": (
                "Obteniendo pedidos {status}, por favor espera..."
            ),
            # UI text
            "select_status_prompt": (
                "Por favor selecciona un estado para ver los pedidos:"
            ),
            "orders_list_header": "<b>Pedidos - {status} ({count})</b>\n\n",
            "no_orders_found": "No se encontraron pedidos con este estado.",
            "text_truncated_suffix": "\n\n[Truncado por longitud]",
            # Order details template
            "order_details_header": "<b>Detalles del Pedido: {order_number}</b>\n\n",
            "order_status_field": "<b>Estado:</b> <i>{status}</i>\n",
            "order_date_field": "<b>Realizado el:</b> {date}\n\n",
            "customer_info_header": (
                "<b>Cliente:</b> {name}\n"
                "<b>Teléfono:</b> <code>{phone}</code>\n"
                "<b>Dirección:</b> <code>{address}</code>\n\n"
            ),
            "items_header": "<b>Artículos:</b>\n",
            "deleted_product_suffix": " ⚠️ <i>(Eliminado - No Cobrado)</i>",
            "item_template": (
                "  - <b>{name}</b>{status}\n"
                "    <code>{quantity} x €{price:.2f} = €{total:.2f}</code>\n"
            ),
            "active_items_total": "<b>Total Artículos Activos: €{total:.2f}</b>\n",
            "deleted_items_total": "<s>Artículos Eliminados: €{total:.2f}</s>\n",
            "final_total": "<b>Total Final: €{total:.2f}</b>\n\n",
            "deleted_items_notice": (
                "⚠️ <i>Los productos eliminados no se cobran. "
                "El cliente paga solo por los artículos activos.</i>"
            ),
            "order_total": "<b>Total: €{total:.2f}</b>",
            "not_available": "N/D",
            # Technical constants
            "max_message_length": "4096",
            "truncate_threshold": "4090",
        }

        # Russian messages
        ru_messages = {
            # Error messages
            "error_query_data_none": "Данные запроса не могут быть пустыми",
            "error_order_not_found": "Не удалось найти этот заказ.",
            "error_invalid_order_id": "Неверный формат ID заказа.",
            "error_status_update_failed": ("Произошла ошибка при обновлении статуса."),
            # Success messages
            "success_status_updated": "Статус заказа обновлен на {status}",
            # Progress messages
            "progress_fetching_orders": (
                "Получение заказов со статусом {status}, пожалуйста подождите..."
            ),
            # UI text
            "select_status_prompt": (
                "Пожалуйста, выберите статус для просмотра заказов:"
            ),
            "orders_list_header": "<b>Заказы - {status} ({count})</b>\n\n",
            "no_orders_found": "Заказы с этим статусом не найдены.",
            "text_truncated_suffix": "\n\n[Обрезано из-за длины]",
            # Order details template
            "order_details_header": "<b>Детали Заказа: {order_number}</b>\n\n",
            "order_status_field": "<b>Статус:</b> <i>{status}</i>\n",
            "order_date_field": "<b>Размещен:</b> {date}\n\n",
            "customer_info_header": (
                "<b>Клиент:</b> {name}\n"
                "<b>Телефон:</b> <code>{phone}</code>\n"
                "<b>Адрес:</b> <code>{address}</code>\n\n"
            ),
            "items_header": "<b>Товары:</b>\n",
            "deleted_product_suffix": " ⚠️ <i>(Удален - Не Оплачивается)</i>",
            "item_template": (
                "  - <b>{name}</b>{status}\n"
                "    <code>{quantity} x ₽{price:.2f} = ₽{total:.2f}</code>\n"
            ),
            "active_items_total": "<b>Итого Активных Товаров: ₽{total:.2f}</b>\n",
            "deleted_items_total": "<s>Удаленные Товары: ₽{total:.2f}</s>\n",
            "final_total": "<b>Итоговая Сумма: ₽{total:.2f}</b>\n\n",
            "deleted_items_notice": (
                "⚠️ <i>Удаленные товары не оплачиваются. "
                "Клиент платит только за активные товары.</i>"
            ),
            "order_total": "<b>Итого: ₽{total:.2f}</b>",
            "not_available": "Н/Д",
            # Technical constants
            "max_message_length": "4096",
            "truncate_threshold": "4090",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
