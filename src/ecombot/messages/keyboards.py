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
            # Admin panel buttons
            "add_category": "➕ Add Category",
            "delete_category": "❌ Delete Category",
            "restore_category": "🔄 Restore Category",
            "add_product": "➕ Add Product",
            "edit_product": "📝 Edit Product",
            "delete_product": "❌ Delete Product",
            "restore_product": "🔄 Restore Product",
            "view_orders": "📦 View Orders",
            "back_to_admin_panel": "⬅️ Back to Admin Panel",
            # Order status buttons
            "pending": "⏳ Pending",
            "processing": "⚙️ Processing",
            "shipped": "🚚 Shipped",
            "completed": "✅ Completed",
            "cancelled": "❌ Cancelled",
            "back_to_filters": "⬅️ Back to Filters",
            "back_to_orders_list": "⬅️ Back to Orders List",
            # Order actions
            "mark_as_processing": "Mark as Processing",
            "mark_as_shipped": "Mark as Shipped",
            "mark_as_completed": "Mark as Completed",
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
            "view_details": "📋 View Details",
            "back_to_orders": "⬅️ Back to Orders",
            # Checkout buttons
            "confirm_order": "✅ Confirm Order",
            "edit_details": "📝 Edit Details",
            "change_address": "📍 Change Address",
        }

        # Spanish messages
        es_messages = {
            # Common buttons
            "cancel": "❌ Cancelar",
            "back": "⬅️ Atrás",
            "yes_delete": "✅ Sí, eliminarlo",
            "no_go_back": "❌ No, volver",
            # Admin panel buttons
            "add_category": "➕ Agregar Categoría",
            "delete_category": "❌ Eliminar Categoría",
            "restore_category": "🔄 Restaurar Categoría",
            "add_product": "➕ Agregar Producto",
            "edit_product": "📝 Editar Producto",
            "delete_product": "❌ Eliminar Producto",
            "restore_product": "🔄 Restaurar Producto",
            "view_orders": "📦 Ver Pedidos",
            "back_to_admin_panel": "⬅️ Volver al Panel Admin",
            # Order status buttons
            "pending": "⏳ Pendiente",
            "processing": "⚙️ Procesando",
            "shipped": "🚚 Enviado",
            "completed": "✅ Completado",
            "cancelled": "❌ Cancelado",
            "back_to_filters": "⬅️ Volver a Filtros",
            "back_to_orders_list": "⬅️ Volver a Lista de Pedidos",
            # Order actions
            "mark_as_processing": "Marcar como Procesando",
            "mark_as_shipped": "Marcar como Enviado",
            "mark_as_completed": "Marcar como Completado",
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
            "view_details": "📋 Ver Detalles",
            "back_to_orders": "⬅️ Volver a Pedidos",
            # Checkout buttons
            "confirm_order": "✅ Confirmar Pedido",
            "edit_details": "📝 Editar Detalles",
            "change_address": "📍 Cambiar Dirección",
        }

        # Russian messages
        ru_messages = {
            # Common buttons
            "cancel": "❌ Отмена",
            "back": "⬅️ Назад",
            "yes_delete": "✅ Да, удалить",
            "no_go_back": "❌ Нет, вернуться",
            # Admin panel buttons
            "add_category": "➕ Добавить Категорию",
            "delete_category": "❌ Удалить Категорию",
            "restore_category": "🔄 Восстановить Категорию",
            "add_product": "➕ Добавить Товар",
            "edit_product": "📝 Редактировать Товар",
            "delete_product": "❌ Удалить Товар",
            "restore_product": "🔄 Восстановить Товар",
            "view_orders": "📦 Просмотр Заказов",
            "back_to_admin_panel": "⬅️ Назад в Админ Панель",
            # Order status buttons
            "pending": "⏳ Ожидает",
            "processing": "⚙️ Обрабатывается",
            "shipped": "🚚 Отправлен",
            "completed": "✅ Завершен",
            "cancelled": "❌ Отменен",
            "back_to_filters": "⬅️ Назад к Фильтрам",
            "back_to_orders_list": "⬅️ Назад к Списку Заказов",
            # Order actions
            "mark_as_processing": "Отметить как Обрабатывается",
            "mark_as_shipped": "Отметить как Отправлен",
            "mark_as_completed": "Отметить как Завершен",
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
            "view_details": "📋 Посмотреть Детали",
            "back_to_orders": "⬅️ Назад к Заказам",
            # Checkout buttons
            "confirm_order": "✅ Подтвердить Заказ",
            "edit_details": "📝 Редактировать Детали",
            "change_address": "📍 Изменить Адрес",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
