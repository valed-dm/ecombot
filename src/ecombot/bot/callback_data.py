"""
Defines CallbackData factories for structured callback query data.

Using CallbackData factories is a best practice in aiogram 3. It helps to
create and parse callback data in a type-safe and readable way, avoiding
"magic strings" and making the code easier to maintain.
"""

from aiogram.filters.callback_data import CallbackData


class AdminCallbackFactory(CallbackData, prefix="admin"):
    """CallbackData for admin panel actions."""

    action: str  # "add_category", "delete_category", "add_product", etc.
    item_id: int | None = None  # For actions that need an ID


class AdminNavCallbackFactory(CallbackData, prefix="admin_nav"):
    """CallbackData for complex admin navigation, like going "back"."""

    action: str  # "back_to_product_list"
    target_message_id: int
    category_id: int


class CatalogCallbackFactory(CallbackData, prefix="catalog"):
    """CallbackData for navigating the product catalog."""

    action: str  # "view_category", "view_product"
    item_id: int  # category_id or product_id


class CartCallbackFactory(CallbackData, prefix="cart"):
    """CallbackData for interacting with the shopping cart."""

    action: str  # "add", "remove", "view"
    item_id: int  # product_id or cart_item_id


class OrderCallbackFactory(CallbackData, prefix="order"):
    """CallbackData for the checkout process and order history."""

    action: str  # "confirm_checkout", "view_details", "back_to_list"
    item_id: int | None = None  # order_id


class EditProductCallbackFactory(CallbackData, prefix="edit_prod"):
    action: str  # "menu", "name", "description", "price", "stock", "change_photo"
    product_id: int


class ConfirmationCallbackFactory(CallbackData, prefix="confirm"):
    action: str  # "delete_product" or "delete_category"
    item_id: int  # product_id or category_id
    confirm: bool  # True if "Yes", False if "No/Cancel"


class CheckoutCallbackFactory(CallbackData, prefix="checkout"):
    """CallbackData for the final order confirmation."""

    action: str  # "confirm", "edit_details", "cancel"


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    action: str  # "edit_phone", "edit_email", "manage_addr", "add_addr", "delete_addr"
    address_id: int | None = None


class DeliveryAdminCallbackFactory(CallbackData, prefix="admin_del"):
    """CallbackData for admin delivery management."""

    action: str  # "menu", "toggle_global", "pp_list", "pp_edit", "dt_list", etc.
    item_id: int | None = None  # For pickup point ID
    value: str | None = None  # For delivery type enum value


class PickupTypeCallbackFactory(CallbackData, prefix="pp_type"):
    type_value: str  # e.g., "pickup_store"


class PickupSelectCallbackFactory(CallbackData, prefix="pp_sel"):
    pickup_point_id: int
