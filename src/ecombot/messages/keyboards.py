"""Keyboard messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class KeyboardMessageManager(BaseMessageManager):
    """Message manager for keyboard button texts."""

    def _load_messages(self) -> None:
        """Load keyboard messages for all supported languages."""

        # English messages
        en_messages = {
            # Common buttons
            "cancel": "❌ Cancel",
            "back": "⬅️ Back",
            "yes_delete": "✅ Yes, delete it",
            "no_go_back": "❌ No, go back",
            "confirm": "✅",
            "cancel_short": "❌",
            # Admin panel buttons
            "add_category": "➕ Add Category",
            "delete_category": "❌ Delete Category",
            "restore_category": "🔄 Restore Category",
            "add_product": "➕ Add Product",
            "edit_product": "📝 Edit Product",
            "delete_product": "❌ Delete Product",
            "restore_product": "🔄 Restore Product",
            "view_orders": "📦 View Orders",
            "manage_delivery": "🚚 Delivery Settings",
            "manage_pickup_points": "📍 Manage Pickup Points",
            "manage_delivery_types": "🚚 Manage Delivery Types",
            "global_delivery_toggle": "Global Delivery: {status_text} {status_icon}",
            "enabled": "Enabled",
            "disabled": "Disabled",
            "back_to_admin_panel": "⬅️ Back to Admin Panel",
            # Order status buttons
            "pending": "⏳ Pending",
            "processing": "⚙️ Accepted",
            "shipped": "🚚 Shipped",
            "pickup_ready": "📦 Ready for Pickup",
            "completed": "✅ Completed",
            "cancelled": "❌ Cancelled",
            "refunded": "💸 Refunded",
            "failed": "⚠️ Failed",
            "back_to_filters": "⬅️ Back to Filters",
            "back_to_orders_list": "⬅️ Back to Orders List",
            # Order actions
            "mark_as_processing": "Accepted",
            "mark_as_shipped": "Shipped",
            "mark_as_pickup_ready": "Ready for Pickup",
            "mark_as_paid": "Paid",
            "mark_as_completed": "Completed",
            "mark_as_refunded": "Refunded",
            "mark_as_failed": "Failed",
            "cancel_order": "Cancel Order",
            # Product editing
            "edit_name": "📝 Name",
            "edit_description": "📄 Description",
            "edit_price": "💰 Price",
            "edit_stock": "📦 Stock",
            "change_photo": "🖼️ Change Photo",
            "back_to_products": "⬅️ Back to Products",
            # Cart buttons
            "add_to_cart": "🛒 Add to Cart",
            "view_cart": "🛒 View Cart",
            "checkout": "✅ Checkout",
            "continue_shopping": "🛍️ Continue Shopping",
            "clear_cart": "🗑️ Clear Cart",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            # Catalog buttons
            "catalog": "🛍️ Catalog",
            "go_to_catalog": "🛍️ Go to Catalog",
            "back_to_catalog": "⬅️ Back to Catalog",
            "back_to_categories": "⬅️ Back to Categories",
            # Profile buttons
            "edit_phone": "📱 Edit Phone",
            "edit_email": "📧 Edit Email",
            "manage_addresses": "📍 Manage Addresses",
            "add_address": "➕ Add Address",
            "set_as_default": "⭐ Set as Default",
            "delete_address": "🗑️ Delete",
            "back_to_profile": "⬅️ Back to Profile",
            "back_to_addresses": "⬅️ Back to Addresses",
            # Orders buttons
            "view_order_number": "🔎 View Order #{order_number}",
            "view_details": "📋 View Details",
            "back_to_orders": "⬅️ Back to Orders",
            # Checkout buttons
            "confirm_order": "✅ Confirm Order",
            "edit_details": "📝 Edit Details",
            "change_address": "📍 Change Address",
            "share_phone": "📱 Share My Phone Number",
        }

        # Spanish messages
        es_messages = {
            # Common buttons
            "cancel": "❌ Cancelar",
            "back": "⬅️ Atrás",
            "yes_delete": "✅ Sí, eliminarlo",
            "no_go_back": "❌ No, volver",
            "confirm": "✅",
            "cancel_short": "❌",
            # Admin panel buttons
            "add_category": "➕ Agregar Categoría",
            "delete_category": "❌ Eliminar Categoría",
            "restore_category": "🔄 Restaurar Categoría",
            "add_product": "➕ Agregar Producto",
            "edit_product": "📝 Editar Producto",
            "delete_product": "❌ Eliminar Producto",
            "restore_product": "🔄 Restaurar Producto",
            "view_orders": "📦 Ver Pedidos",
            "manage_delivery": "🚚 Configuración de Entrega",
            "manage_pickup_points": "📍 Gestionar Puntos de Recogida",
            "manage_delivery_types": "🚚 Gestionar Tipos de Entrega",
            "global_delivery_toggle": "Entrega Global: {status_text} {status_icon}",
            "enabled": "Habilitado",
            "disabled": "Deshabilitado",
            "back_to_admin_panel": "⬅️ Volver al Panel Admin",
            # Order status buttons
            "pending": "⏳ Pendiente",
            "processing": "⚙️ Aceptado",
            "shipped": "🚚 Enviado",
            "pickup_ready": "📦 Listo para recoger",
            "completed": "✅ Completado",
            "cancelled": "❌ Cancelado",
            "refunded": "💸 Reembolsado",
            "failed": "⚠️ Fallido",
            "back_to_filters": "⬅️ Volver a Filtros",
            "back_to_orders_list": "⬅️ Volver a Lista de Pedidos",
            # Order actions
            "mark_as_processing": "Aceptado",
            "mark_as_shipped": "Enviado",
            "mark_as_pickup_ready": "Listo para Recoger",
            "mark_as_paid": "Pagado",
            "mark_as_completed": "Completado",
            "mark_as_refunded": "Reembolsado",
            "mark_as_failed": "Fallido",
            "cancel_order": "Cancelar Pedido",
            # Product editing
            "edit_name": "📝 Nombre",
            "edit_description": "📄 Descripción",
            "edit_price": "💰 Precio",
            "edit_stock": "📦 Stock",
            "change_photo": "🖼️ Cambiar Foto",
            "back_to_products": "⬅️ Volver a Productos",
            # Cart buttons
            "add_to_cart": "🛒 Agregar al Carrito",
            "view_cart": "🛒 Ver Carrito",
            "checkout": "✅ Finalizar Compra",
            "continue_shopping": "🛍️ Seguir Comprando",
            "clear_cart": "🗑️ Vaciar Carrito",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            # Catalog buttons
            "catalog": "🛍️ Catálogo",
            "go_to_catalog": "🛍️ Ir al Catálogo",
            "back_to_catalog": "⬅️ Volver al Catálogo",
            "back_to_categories": "⬅️ Volver a Categorías",
            # Profile buttons
            "edit_phone": "📱 Editar Teléfono",
            "edit_email": "📧 Editar Email",
            "manage_addresses": "📍 Gestionar Direcciones",
            "add_address": "➕ Agregar Dirección",
            "set_as_default": "⭐ Establecer por Defecto",
            "delete_address": "🗑️ Eliminar",
            "back_to_profile": "⬅️ Volver al Perfil",
            "back_to_addresses": "⬅️ Volver a Direcciones",
            # Orders buttons
            "view_order_number": "🔎 Ver Pedido #{order_number}",
            "view_details": "📋 Ver Detalles",
            "back_to_orders": "⬅️ Volver a Pedidos",
            # Checkout buttons
            "confirm_order": "✅ Confirmar Pedido",
            "edit_details": "📝 Editar Detalles",
            "change_address": "📍 Cambiar Dirección",
            "share_phone": "📱 Compartir mi número",
        }

        # Russian messages
        ru_messages = {
            # Common buttons
            "cancel": "❌ Отмена",
            "back": "⬅️ Назад",
            "yes_delete": "✅ Да, удалить",
            "no_go_back": "❌ Нет, вернуться",
            "confirm": "✅",
            "cancel_short": "❌",
            # Admin panel buttons
            "add_category": "➕ Добавить Категорию",
            "delete_category": "❌ Удалить Категорию",
            "restore_category": "🔄 Восстановить Категорию",
            "add_product": "➕ Добавить Товар",
            "edit_product": "📝 Редактировать Товар",
            "delete_product": "❌ Удалить Товар",
            "restore_product": "🔄 Восстановить Товар",
            "view_orders": "📦 Просмотр Заказов",
            "manage_delivery": "🚚 Настройки Доставки",
            "manage_pickup_points": "📍 Управление Пунктами Выдачи",
            "manage_delivery_types": "🚚 Управление Типами Доставки",
            "global_delivery_toggle": (
                "Глобальная Доставка: {status_text} {status_icon}"
            ),
            "enabled": "Включено",
            "disabled": "Выключено",
            "back_to_admin_panel": "⬅️ Назад в Админ Панель",
            # Order status buttons
            "pending": "⏳ Ожидает",
            "processing": "⚙️ Принят",
            "shipped": "🚚 Отправлен",
            "pickup_ready": "📦 Готов к выдаче",
            "completed": "✅ Завершен",
            "cancelled": "❌ Отменен",
            "refunded": "💸 Возвращен",
            "failed": "⚠️ Ошибка",
            "back_to_filters": "⬅️ Назад к Фильтрам",
            "back_to_orders_list": "⬅️ Назад к Списку Заказов",
            # Order actions
            "mark_as_processing": "Принят",
            "mark_as_shipped": "Отправлен",
            "mark_as_pickup_ready": "Готов к выдаче",
            "mark_as_paid": "Оплачен",
            "mark_as_completed": "Завершен",
            "mark_as_refunded": "Возвращен",
            "mark_as_failed": "Ошибка",
            "cancel_order": "Отменить Заказ",
            # Product editing
            "edit_name": "📝 Название",
            "edit_description": "📄 Описание",
            "edit_price": "💰 Цена",
            "edit_stock": "📦 Склад",
            "change_photo": "🖼️ Изменить Фото",
            "back_to_products": "⬅️ Назад к Товарам",
            # Cart buttons
            "add_to_cart": "🛒 Добавить в Корзину",
            "view_cart": "🛒 Посмотреть Корзину",
            "checkout": "✅ Оформить Заказ",
            "continue_shopping": "🛍️ Продолжить Покупки",
            "clear_cart": "🗑️ Очистить Корзину",
            "increase_quantity": "➕",
            "decrease_quantity": "➖",
            "remove_item": "❌",
            # Catalog buttons
            "catalog": "🛍️ Каталог",
            "go_to_catalog": "🛍️ Перейти к Каталогу",
            "back_to_catalog": "⬅️ Назад к Каталогу",
            "back_to_categories": "⬅️ Назад к Категориям",
            # Profile buttons
            "edit_phone": "📱 Редактировать Телефон",
            "edit_email": "📧 Редактировать Email",
            "manage_addresses": "📍 Управление Адресами",
            "add_address": "➕ Добавить Адрес",
            "set_as_default": "⭐ Установить по Умолчанию",
            "delete_address": "🗑️ Удалить",
            "back_to_profile": "⬅️ Назад к Профилю",
            "back_to_addresses": "⬅️ Назад к Адресам",
            # Orders buttons
            "view_order_number": "🔎 Посмотреть заказ №{order_number}",
            "view_details": "📋 Посмотреть Детали",
            "back_to_orders": "⬅️ Назад к Заказам",
            # Checkout buttons
            "confirm_order": "✅ Подтвердить Заказ",
            "edit_details": "📝 Редактировать Детали",
            "change_address": "📍 Изменить Адрес",
            "share_phone": "📱 Поделиться номером",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
