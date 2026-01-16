"""Delivery-related messages."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class DeliveryMessageManager(BaseMessageManager):
    """Message manager for delivery settings and flows."""

    def _load_messages(self) -> None:
        en_messages = {
            "menu_text": (
                "<b>📦 Delivery Management</b>\n\n"
                "Configure how customers receive their orders.\n"
                "Current Mode: <b>{current_mode}</b>"
            ),
            "mode_delivery_pickup": "Delivery & Pickup",
            "mode_pickup_only": "Pickup Only",
            "toggled_msg": "Delivery mode set to: {status}",
            # Pickup Points
            "pp_list_text": "<b>📍 Pickup Points</b>\nSelect a point to toggle availability or delete.",
            "pp_not_found": "Pickup point not found.",
            "pp_details": "<b>📍 {name}</b>\n\nAddress: {address}\nType: {type}\nHours: {hours}\nStatus: {status}",
            "status_active": "Active ✅",
            "status_inactive": "Inactive ❌",
            "status_updated": "Status updated.",
            "pp_deleted": "Pickup point deleted.",
            "no_pp_found": "No pickup points found.",
            "pp_addresses_header": "<b>📍 Pickup Point Addresses:</b>\n",
            "enter_pp_name": "Enter the <b>Name</b> for the new pickup point:",
            "enter_pp_address": "Enter the <b>Full Address</b>:",
            "select_pp_type": "Select the <b>Pickup Type</b>:",
            "invalid_type": "Invalid type.",
            "enter_pp_hours": "Selected: {type}\n\nEnter <b>Working Hours</b> (e.g., 'Mon-Fri 9-18'):",
            "pp_created": "✅ Pickup point <b>{name}</b> created successfully!",
            # Delivery Types
            "dt_list_text": "<b>🚚 Delivery Types</b>\nTap to toggle availability.\n⚪ = Inactive/Not Configured\n✅ = Active",
            "invalid_dt": "Invalid delivery type.",
            "dt_toggled": "{type} is now {status}",
            "active": "Active",
            "inactive": "Inactive",
            # DeliveryType Enum Translations
            "delivery_pickup_store": "Store Pickup",
            "delivery_pickup_locker": "Locker Pickup",
            "delivery_pickup_curbside": "Curbside Pickup",
            "delivery_hyperlocal_instant": "Instant Delivery",
            "delivery_hyperlocal_neighborhood": "Neighborhood Delivery",
            "delivery_local_same_day": "Local Same Day",
            "delivery_local_next_day": "Local Next Day",
            "delivery_regional_standard": "Regional Standard",
            "delivery_regional_express": "Regional Express",
            "delivery_national_standard": "National Standard",
            "delivery_national_express": "National Express",
            "delivery_national_priority": "National Priority",
            "delivery_special_scheduled": "Scheduled Delivery",
            "delivery_special_bulk": "Bulk Delivery",
        }

        es_messages = {
            "menu_text": (
                "<b>📦 Gestión de Entregas</b>\n\n"
                "Configure cómo reciben los pedidos los clientes.\n"
                "Modo Actual: <b>{current_mode}</b>"
            ),
            "mode_delivery_pickup": "Entrega y Recogida",
            "mode_pickup_only": "Solo Recogida",
            "toggled_msg": "Modo de entrega establecido a: {status}",
            # Pickup Points
            "pp_list_text": "<b>📍 Puntos de Recogida</b>\nSeleccione un punto para cambiar disponibilidad o eliminar.",
            "pp_not_found": "Punto de recogida no encontrado.",
            "pp_details": "<b>📍 {name}</b>\n\nDirección: {address}\nTipo: {type}\nHorario: {hours}\nEstado: {status}",
            "status_active": "Activo ✅",
            "status_inactive": "Inactivo ❌",
            "status_updated": "Estado actualizado.",
            "pp_deleted": "Punto de recogida eliminado.",
            "no_pp_found": "No se encontraron puntos de recogida.",
            "pp_addresses_header": "<b>📍 Direcciones de Puntos de Recogida:</b>\n",
            "enter_pp_name": "Ingrese el <b>Nombre</b> del nuevo punto de recogida:",
            "enter_pp_address": "Ingrese la <b>Dirección Completa</b>:",
            "select_pp_type": "Seleccione el <b>Tipo de Recogida</b>:",
            "invalid_type": "Tipo inválido.",
            "enter_pp_hours": "Seleccionado: {type}\n\nIngrese <b>Horario de Atención</b> (ej. 'Lun-Vie 9-18'):",
            "pp_created": "✅ ¡Punto de recogida <b>{name}</b> creado exitosamente!",
            # Delivery Types
            "dt_list_text": "<b>🚚 Tipos de Entrega</b>\nToque para cambiar disponibilidad.\n⚪ = Inactivo/No Configurado\n✅ = Activo",
            "invalid_dt": "Tipo de entrega inválido.",
            "dt_toggled": "{type} ahora está {status}",
            "active": "Activo",
            "inactive": "Inactivo",
            # DeliveryType Enum Translations
            "delivery_pickup_store": "Recogida en Tienda",
            "delivery_pickup_locker": "Recogida en Taquilla",
            "delivery_pickup_curbside": "Recogida en Acera",
            "delivery_hyperlocal_instant": "Entrega Instantánea",
            "delivery_hyperlocal_neighborhood": "Entrega Vecinal",
            "delivery_local_same_day": "Local Mismo Día",
            "delivery_local_next_day": "Local Día Siguiente",
            "delivery_regional_standard": "Regional Estándar",
            "delivery_regional_express": "Regional Exprés",
            "delivery_national_standard": "Nacional Estándar",
            "delivery_national_express": "Nacional Exprés",
            "delivery_national_priority": "Nacional Prioritario",
            "delivery_special_scheduled": "Entrega Programada",
            "delivery_special_bulk": "Entrega a Granel",
        }

        ru_messages = {
            "menu_text": (
                "<b>📦 Управление Доставкой</b>\n\n"
                "Настройте способы получения заказов клиентами.\n"
                "Текущий Режим: <b>{current_mode}</b>"
            ),
            "mode_delivery_pickup": "Доставка и Самовывоз",
            "mode_pickup_only": "Только Самовывоз",
            "toggled_msg": "Режим доставки установлен: {status}",
            # Pickup Points
            "pp_list_text": "<b>📍 Пункты Выдачи</b>\nВыберите пункт для изменения статуса или удаления.",
            "pp_not_found": "Пункт выдачи не найден.",
            "pp_details": "<b>📍 {name}</b>\n\nАдрес: {address}\nТип: {type}\nЧасы работы: {hours}\nСтатус: {status}",
            "status_active": "Активен ✅",
            "status_inactive": "Неактивен ❌",
            "status_updated": "Статус обновлен.",
            "pp_deleted": "Пункт выдачи удален.",
            "no_pp_found": "Пункты выдачи не найдены.",
            "pp_addresses_header": "<b>📍 Адреса Пунктов Выдачи:</b>\n",
            "enter_pp_name": "Введите <b>Название</b> нового пункта выдачи:",
            "enter_pp_address": "Введите <b>Полный Адрес</b>:",
            "select_pp_type": "Выберите <b>Тип Пункта</b>:",
            "invalid_type": "Неверный тип.",
            "enter_pp_hours": "Выбрано: {type}\n\nВведите <b>Часы Работы</b> (например, 'Пн-Пт 9-18'):",
            "pp_created": "✅ Пункт выдачи <b>{name}</b> успешно создан!",
            # Delivery Types
            "dt_list_text": "<b>🚚 Типы Доставки</b>\nНажмите для переключения доступности.\n⚪ = Неактивно/Не настроено\n✅ = Активно",
            "invalid_dt": "Неверный тип доставки.",
            "dt_toggled": "{type} теперь {status}",
            "active": "Активен",
            "inactive": "Неактивен",
            # DeliveryType Enum Translations
            "delivery_pickup_store": "Самовывоз из магазина",
            "delivery_pickup_locker": "Постамат",
            "delivery_pickup_curbside": "Выдача на улице",
            "delivery_hyperlocal_instant": "Мгновенная доставка",
            "delivery_hyperlocal_neighborhood": "Доставка по району",
            "delivery_local_same_day": "Локальная (в тот же день)",
            "delivery_local_next_day": "Локальная (на след. день)",
            "delivery_regional_standard": "Региональная (Стандарт)",
            "delivery_regional_express": "Региональная (Экспресс)",
            "delivery_national_standard": "По стране (Стандарт)",
            "delivery_national_express": "По стране (Экспресс)",
            "delivery_national_priority": "По стране (Приоритет)",
            "delivery_special_scheduled": "Запланированная доставка",
            "delivery_special_bulk": "Оптовая доставка",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
