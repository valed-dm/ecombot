"""Delivery-related messages."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class DeliveryMessageManager(BaseMessageManager):
    """Message manager for delivery settings and flows."""

    def _load_messages(self) -> None:
        en_messages = {
            "menu_text": "<b>📦 Delivery Management</b>\n\nConfigure how customers receive their orders.\nCurrent Mode: <b>{current_mode}</b>",
            "mode_delivery_pickup": "Delivery & Pickup",
            "mode_pickup_only": "Pickup Only",
            "toggled_msg": "Delivery mode set to: {status}",
        }

        es_messages = {
            "menu_text": "<b>📦 Gestión de Entregas</b>\n\nConfigure cómo reciben los pedidos los clientes.\nModo Actual: <b>{current_mode}</b>",
            "mode_delivery_pickup": "Entrega y Recogida",
            "mode_pickup_only": "Solo Recogida",
            "toggled_msg": "Modo de entrega establecido a: {status}",
        }

        ru_messages = {
            "menu_text": "<b>📦 Управление Доставкой</b>\n\nНастройте способы получения заказов клиентами.\nТекущий Режим: <b>{current_mode}</b>",
            "mode_delivery_pickup": "Доставка и Самовывоз",
            "mode_pickup_only": "Только Самовывоз",
            "toggled_msg": "Режим доставки установлен: {status}",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }