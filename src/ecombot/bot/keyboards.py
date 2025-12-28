"""
Defines all inline and reply keyboards used throughout the bot.

This module centralizes the UI components, making it easy to reuse keyboards
across different handlers and maintain a consistent user experience.
"""

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.schemas.dto import CartDTO
from ecombot.schemas.dto import CategoryDTO
from ecombot.schemas.dto import DeliveryAddressDTO
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.dto import ProductDTO
from ecombot.schemas.dto import UserProfileDTO

from ..schemas.enums import OrderStatus
from .callback_data import AdminCallbackFactory
from .callback_data import AdminNavCallbackFactory
from .callback_data import CartCallbackFactory
from .callback_data import CatalogCallbackFactory
from .callback_data import CheckoutCallbackFactory
from .callback_data import ConfirmationCallbackFactory
from .callback_data import EditProductCallbackFactory
from .callback_data import OrderCallbackFactory
from .callback_data import ProfileCallbackFactory


def get_catalog_categories_keyboard(
    categories: list[CategoryDTO],
) -> InlineKeyboardMarkup:
    """Builds a keyboard for the top-level categories."""
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=CatalogCallbackFactory(
                action="view_category", item_id=category.id
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_catalog_products_keyboard(products: list[ProductDTO]) -> InlineKeyboardMarkup:
    """Builds a keyboard for the list of products in a category."""
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} - ${product.price:.2f}",
            callback_data=CatalogCallbackFactory(
                action="view_product", item_id=product.id
            ),
        )
    builder.button(
        text="⬅️ Back to Categories",
        callback_data=CatalogCallbackFactory(action="back_to_main", item_id=0),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_product_details_keyboard(product: ProductDTO) -> InlineKeyboardMarkup:
    """Builds a keyboard for a single product view."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Add to Cart",
        callback_data=CartCallbackFactory(action="add", item_id=product.id),
    )
    builder.button(
        text="⬅️ Back to Products",
        callback_data=CatalogCallbackFactory(
            action="view_category", item_id=product.category.id
        ),
    )
    return builder.as_markup()


def get_cart_keyboard(cart: CartDTO) -> InlineKeyboardMarkup:
    """
    Builds an interactive keyboard for the shopping cart.
    Features a compact, single-row design for item actions.
    """
    builder = InlineKeyboardBuilder()

    for item in cart.items:
        builder.row(
            InlineKeyboardButton(
                text="➖",
                callback_data=CartCallbackFactory(
                    action="decrease", item_id=item.id
                ).pack(),
            ),
            InlineKeyboardButton(text=f"{item.quantity}", callback_data="do_nothing"),
            InlineKeyboardButton(
                text=f"{item.product.name}",
                callback_data=CatalogCallbackFactory(
                    action="view_product", item_id=item.product.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=CartCallbackFactory(
                    action="increase", item_id=item.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=CartCallbackFactory(
                    action="remove", item_id=item.id
                ).pack(),
            ),
        )

    action_buttons = []
    if cart.items:
        action_buttons.append(
            InlineKeyboardButton(text="✅ Checkout", callback_data="checkout_start")
        )
    action_buttons.append(
        InlineKeyboardButton(
            text="🛍️ Catalog",
            callback_data=CatalogCallbackFactory(
                action="back_to_main", item_id=0
            ).pack(),
        )
    )
    builder.row(*action_buttons)

    return builder.as_markup()


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Builds the main keyboard for the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Add Category",
        callback_data=AdminCallbackFactory(action="add_category")
    )
    builder.button(
        text="❌ Delete Category",
        callback_data=AdminCallbackFactory(action="delete_category")
    )
    builder.button(
        text="➕ Add Product",
        callback_data=AdminCallbackFactory(action="add_product")
    )
    builder.button(
        text="📝 Edit Product",
        callback_data=AdminCallbackFactory(action="edit_product")
    )
    builder.button(
        text="❌ Delete Product",
        callback_data=AdminCallbackFactory(action="delete_product")
    )
    builder.button(
        text="📦 View Orders",
        callback_data=AdminCallbackFactory(action="view_orders")
    )
    builder.adjust(2, 3, 1)
    return builder.as_markup()


def get_admin_order_filters_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for filtering orders in the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⏳ Pending",
        callback_data=f"admin_order_filter:{OrderStatus.PENDING.value}",
    )
    builder.button(
        text="⚙️ Processing",
        callback_data=f"admin_order_filter:{OrderStatus.PROCESSING.value}",
    )
    builder.button(
        text="🚚 Shipped",
        callback_data=f"admin_order_filter:{OrderStatus.SHIPPED.value}",
    )
    builder.button(
        text="✅ Completed",
        callback_data=f"admin_order_filter:{OrderStatus.COMPLETED.value}",
    )
    builder.button(
        text="❌ Cancelled",
        callback_data=f"admin_order_filter:{OrderStatus.CANCELLED.value}",
    )
    builder.button(
        text="⬅️ Back to Admin Panel",
        callback_data=AdminCallbackFactory(action="back_main"),
    )
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def get_admin_order_details_keyboard(order: OrderDTO) -> InlineKeyboardMarkup:
    """Builds the action keyboard for an admin viewing an order's details."""
    builder = InlineKeyboardBuilder()

    # Logic to show the NEXT valid status, not all statuses
    if order.status == OrderStatus.PENDING:
        builder.button(
            text="Mark as Processing",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.PROCESSING.value}",
        )
    elif order.status == OrderStatus.PROCESSING:
        builder.button(
            text="Mark as Shipped",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.SHIPPED.value}",
        )
    elif order.status == OrderStatus.SHIPPED:
        builder.button(
            text="Mark as Completed",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.COMPLETED.value}",
        )

    if order.status not in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        builder.button(
            text="Cancel Order",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.CANCELLED.value}",
        )

    builder.button(
        text="⬅️ Back to Orders List",
        callback_data=f"admin_order_filter:{order.status.value}",
    )
    builder.adjust(1)
    return builder.as_markup()


def get_delete_confirmation_keyboard(
    action: str,
    item_id: int,
) -> InlineKeyboardMarkup:
    """Builds a generic Yes/No confirmation keyboard for deletion."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Yes, delete it",
        callback_data=ConfirmationCallbackFactory(
            action=action,
            item_id=item_id,
            confirm=True,
        ),
    )
    builder.button(
        text="❌ No, go back",
        callback_data=ConfirmationCallbackFactory(
            action=action,
            item_id=item_id,
            confirm=False,
        ),
    )
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """A simple keyboard with a single 'Cancel' button."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Cancel", callback_data="cancel_fsm")
    return builder.as_markup()


def get_edit_product_menu_keyboard(
    product_id: int,
    product_list_message_id: int,  # The ID of the message to go back to
    category_id: int,
) -> InlineKeyboardMarkup:
    """Builds a keyboard for choosing which product attribute to edit."""
    builder = InlineKeyboardBuilder()

    fields_to_edit = {
        "name": "📝 Name",
        "description": "📄 Description",
        "price": "💰 Price",
        "stock": "📦 Stock",
    }

    for field, text in fields_to_edit.items():
        builder.button(
            text=text,
            callback_data=EditProductCallbackFactory(
                action=field, product_id=product_id
            ),
        )

    builder.button(
        text="🖼️ Change Photo",
        callback_data=EditProductCallbackFactory(
            action="change_photo", product_id=product_id
        ),
    )

    builder.button(
        text="⬅️ Back to Products",
        callback_data=AdminNavCallbackFactory(
            action="back_to_product_list",
            target_message_id=product_list_message_id,
            category_id=category_id,
        ),
    )

    builder.adjust(2)
    return builder.as_markup()


def get_request_contact_keyboard() -> ReplyKeyboardMarkup:
    """
    Builds a reply keyboard with a single button to request the user's contact.
    This is a special button type that prompts the user to share their phone number.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Share My Phone Number", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_checkout_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Builds the final Yes/No keyboard for confirming the order,
    used in the "slow path" FSM.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅",
        callback_data=CheckoutCallbackFactory(action="confirm"),
    )
    builder.button(
        text="❌",
        callback_data=CheckoutCallbackFactory(action="cancel"),
    )

    return builder.as_markup()


def get_fast_checkout_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Builds the keyboard for the 'fast path' checkout confirmation."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Confirm & Place Order",
        callback_data=CheckoutCallbackFactory(action="confirm"),
    )
    builder.button(
        text="✏️ Edit Details",
        callback_data=CheckoutCallbackFactory(action="edit_details"),
    )
    builder.button(
        text="❌ Cancel",
        callback_data=CheckoutCallbackFactory(action="cancel"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📞 Edit Phone",
        callback_data=ProfileCallbackFactory(action="edit_phone"),
    )
    builder.button(
        text="✉️ Edit Email",
        callback_data=ProfileCallbackFactory(action="edit_email"),
    )
    builder.button(
        text="📍 Manage Addresses",
        callback_data=ProfileCallbackFactory(action="manage_addr"),
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def get_address_management_keyboard(
    addresses: list[DeliveryAddressDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for addr in addresses:
        # Add a star for the default address
        prefix = "⭐️ Default: " if addr.is_default else "📍"

        builder.row(
            InlineKeyboardButton(
                text=f"{prefix} {addr.address_label}",
                callback_data="do_nothing",
            )
        )
        action_row = []

        if not addr.is_default:
            action_row.append(
                InlineKeyboardButton(
                    text="Set as Default",
                    callback_data=ProfileCallbackFactory(
                        action="set_default_addr", address_id=addr.id
                    ).pack(),
                )
            )
        action_row.append(
            InlineKeyboardButton(
                text="❌ Delete",
                callback_data=ProfileCallbackFactory(
                    action="delete_addr", address_id=addr.id
                ).pack(),
            )
        )
        builder.row(*action_row)

    builder.button(
        text="➕ Add New Address",
        callback_data=ProfileCallbackFactory(action="add_addr"),
    )
    builder.button(text="⬅️ Back to Profile", callback_data="profile_back_main")
    return builder.as_markup()


def get_orders_list_keyboard(orders: list[OrderDTO]) -> InlineKeyboardMarkup:
    """
    Builds a keyboard for the order history list, with a 'View Details'
    button for each.
    """
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(
            text=f"🔎 View Order #{order.order_number}",
            callback_data=OrderCallbackFactory(action="view_details", item_id=order.id),
        )
    builder.adjust(1)
    return builder.as_markup()


def get_order_details_keyboard() -> InlineKeyboardMarkup:
    """Builds a simple keyboard with a 'Back to Orders' button."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Back to Order History",
        callback_data=OrderCallbackFactory(action="back_to_list"),
    )
    return builder.as_markup()
