"""Order-related messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class OrdersMessageManager(BaseMessageManager):
    """Message manager for order-related messages."""

    def _load_messages(self) -> None:
        """Load order messages for all supported languages."""

        # English messages
        en_messages = {
            "order_history_header": "<b>📦 Your Order History:</b>\n\n",
            "no_orders_message": "You haven't placed any orders yet.",
            "order_list_button": "{order_id} - {status} ({total:.2f})",
            "order_details_header": "<b>🧾 Order Details #{order_id}</b>\n\n",
            "order_date_line": "<b>Date:</b> {date}\n",
            "order_address_line": "<b>Shipping Address:</b>\n<code>{address}</code>\n",
            "status_line": "<b>Status:</b> {status}\n",
            "order_items_header": "\n<b>Items:</b>\n",
            "order_item_template": (
                "• {name} x{quantity} — {price:.2f} (Total: {total:.2f})\n"
            ),
            "deleted_product_suffix": " (No longer available)",
            "total_label": "<b>Total: ${total:.2f}</b>",
            "active_items_total": "<b>Active Items Total: ${total:.2f}</b>\n",
            "deleted_items_total": "<b>Unavailable Items Total: ${total:.2f}</b>\n",
            "total_paid": "<b>Total Paid: ${total:.2f}</b>",
            "date_format": "%Y-%m-%d %H:%M",
            # Notifications
            "notification_processing": (
                "✅ <b>Order Status Updated: {status}</b>\n\n"
                "Your order <code>{order_number}</code> has been accepted. "
                "We'll notify you again once it has shipped."
            ),
            "notification_pickup_ready": (
                "📦 <b>Order Status Updated: {status}</b>\n\n"
                "Your order <code>{order_number}</code> is ready for pickup!"
            ),
            "notification_paid": (
                "💰 <b>Order Status Updated: {status}</b>\n\n"
                "Payment received for order <code>{order_number}</code>."
            ),
            "notification_shipped": (
                "🚚 <b>Order Status Updated: {status}</b>\n\n"
                "Your order <code>{order_number}</code> has been shipped. "
                "You can track its progress in your /orders menu."
            ),
            "notification_completed": (
                "🎉 <b>Your Order is Complete!</b>\n\n"
                "Thank you for your purchase! Order: <code>{order_number}</code>"
            ),
            "notification_cancelled": (
                "❌ <b>Order Status Updated: {status}</b>\n\n"
                "Your order <code>{order_number}</code> has been successfully "
                "cancelled."
            ),
            "notification_refunded": (
                "💸 <b>Order Status Updated: {status}</b>\n\n"
                "Your order <code>{order_number}</code> has been refunded."
            ),
            "notification_failed": (
                "⚠️ <b>Order Status Updated: {status}</b>\n\n"
                "Processing for order <code>{order_number}</code> has failed."
            ),
        }

        # Spanish messages
        es_messages = {
            "order_history_header": "<b>📦 Tu Historial de Pedidos:</b>\n\n",
            "no_orders_message": "Aún no has realizado ningún pedido.",
            "order_list_button": "{order_id} - {status} ({total:.2f})",
            "order_details_header": "<b>🧾 Detalles del Pedido #{order_id}</b>\n\n",
            "order_date_line": "<b>Fecha:</b> {date}\n",
            "order_address_line": (
                "<b>Dirección de Envío:</b>\n<code>{address}</code>\n"
            ),
            "status_line": "<b>Estado:</b> {status}\n",
            "order_items_header": "\n<b>Artículos:</b>\n",
            "order_item_template": (
                "• {name} x{quantity} — {price:.2f} (Total: {total:.2f})\n"
            ),
            "deleted_product_suffix": " (Ya no disponible)",
            "total_label": "<b>Total: €{total:.2f}</b>",
            "active_items_total": "<b>Total Artículos Activos: €{total:.2f}</b>\n",
            "deleted_items_total": (
                "<b>Total Artículos No Disponibles: €{total:.2f}</b>\n"
            ),
            "total_paid": "<b>Total Pagado: €{total:.2f}</b>",
            "date_format": "%d/%m/%Y %H:%M",
            # Notifications
            "notification_processing": (
                "✅ <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "Tu pedido <code>{order_number}</code> ha sido aceptado. "
                "Te notificaremos nuevamente cuando haya sido enviado."
            ),
            "notification_pickup_ready": (
                "📦 <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "¡Tu pedido <code>{order_number}</code> está listo para recoger!"
            ),
            "notification_paid": (
                "💰 <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "Pago recibido para el pedido <code>{order_number}</code>."
            ),
            "notification_shipped": (
                "🚚 <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "Tu pedido <code>{order_number}</code> ha sido enviado. "
                "Puedes seguir su progreso en tu menú /orders."
            ),
            "notification_completed": (
                "🎉 <b>¡Tu Pedido está Completo!</b>\n\n"
                "¡Gracias por tu compra! Pedido: <code>{order_number}</code>"
            ),
            "notification_cancelled": (
                "❌ <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "Tu pedido <code>{order_number}</code> ha sido cancelado exitosamente."
            ),
            "notification_refunded": (
                "💸 <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "Tu pedido <code>{order_number}</code> ha sido reembolsado."
            ),
            "notification_failed": (
                "⚠️ <b>Estado del Pedido Actualizado: {status}</b>\n\n"
                "El procesamiento del pedido <code>{order_number}</code> ha fallado."
            ),
        }

        # Russian messages (Assuming similar structure, placeholders for brevity if
        # needed, but providing full for completeness)
        ru_messages = {
            "order_history_header": "<b>📦 История ваших заказов:</b>\n\n",
            "no_orders_message": "Вы еще не делали заказов.",
            "order_list_button": "{order_id} - {status} ({total:.2f})",
            "order_details_header": "<b>🧾 Детали заказа #{order_id}</b>\n\n",
            "order_date_line": "<b>Дата:</b> {date}\n",
            "order_address_line": "<b>Адрес доставки:</b>\n<code>{address}</code>\n",
            "status_line": "<b>Статус:</b> {status}\n",
            "order_items_header": "\n<b>Товары:</b>\n",
            "order_item_template": (
                "• {name} x{quantity} — {price:.2f} (Итого: {total:.2f})\n"
            ),
            "deleted_product_suffix": " (Больше не доступен)",
            "total_label": "<b>Итого: {total:.2f}₽</b>",
            "active_items_total": "<b>Итого (доступные): {total:.2f}₽</b>\n",
            "deleted_items_total": "<b>Итого (недоступные): {total:.2f}₽</b>\n",
            "total_paid": "<b>Всего оплачено: {total:.2f}₽</b>",
            "date_format": "%d.%m.%Y %H:%M",
            "notification_processing": (
                "✅ <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ваш заказ <code>{order_number}</code> принят."
            ),
            "notification_pickup_ready": (
                "📦 <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ваш заказ <code>{order_number}</code> готов к выдаче!"
            ),
            "notification_paid": (
                "💰 <b>Статус заказа обновлен: {status}</b>\n\n"
                "Оплата получена для заказа <code>{order_number}</code>."
            ),
            "notification_shipped": (
                "🚚 <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ваш заказ <code>{order_number}</code> отправлен."
            ),
            "notification_completed": (
                "🎉 <b>Заказ выполнен!</b>\n\n"
                "Спасибо за покупку! Заказ: <code>{order_number}</code>"
            ),
            "notification_cancelled": (
                "❌ <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ваш заказ <code>{order_number}</code> отменен."
            ),
            "notification_refunded": (
                "💸 <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ваш заказ <code>{order_number}</code> был возвращен."
            ),
            "notification_failed": (
                "⚠️ <b>Статус заказа обновлен: {status}</b>\n\n"
                "Ошибка обработки заказа <code>{order_number}</code>."
            ),
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
