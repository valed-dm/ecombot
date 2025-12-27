"""
Admin Handlers for Order Management.

This module contains the handlers for the admin workflow of viewing,
filtering, and updating the status of customer orders.
"""

from html import escape

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.filters.is_admin import IsAdmin
from ecombot.bot.handlers.admin import send_main_admin_panel
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.db import crud
from ecombot.logging_setup import logger
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus
from ecombot.services import notification_service
from ecombot.services import order_service


class InvalidQueryDataError(ValueError):
    """Raised when query data is invalid or missing."""

    pass


# =============================================================================
# Router and Middleware Setup
# =============================================================================


router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.callback_query.middleware(MessageInteractionMiddleware())


# =============================================================================
# Helper Functions
# =============================================================================


async def send_order_details_view(message: Message, order: OrderDTO):
    """
    Generates and sends the detailed view for a single order for an admin.
    """
    text_parts = [
        f"<b>Order Details: {escape(order.order_number)}</b>\n\n",
        f"<b>Status:</b> <i>{order.status.capitalize()}</i>\n",
        f"<b>Placed on:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n",
        f"<b>Customer:</b> {escape(order.contact_name or 'N/A')}\n",
        f"<b>Phone:</b> <code>{escape(order.phone or 'N/A')}</code>\n",
        f"<b>Address:</b> <code>{escape(order.address or 'N/A')}</code>\n\n",
        "<b>Items:</b>\n"
    ]
    
    for item in order.items:
        item_total = item.price * item.quantity
        text_parts.extend([
            f"  - <b>{escape(item.product.name)}</b>\n",
            f"    <code>{item.quantity} x ${item.price:.2f}",
            f" = ${item_total:.2f}</code>\n"
        ])
    
    text_parts.append(f"\n<b>Total: ${order.total_price:.2f}</b>")
    text = "".join(text_parts)

    keyboard = keyboards.get_admin_order_details_keyboard(order)
    await message.edit_text(text, reply_markup=keyboard)


# =============================================================================
# Navigation Handlers
# =============================================================================


@router.callback_query(F.data == "admin_back_main")
async def back_to_main_admin_panel_handler(
    query: CallbackQuery, callback_message: Message
):
    """
    Handles the "Back to Admin Panel" button from any order management view.
    """

    await send_main_admin_panel(callback_message)
    await query.answer()


# =============================================================================
# Order Management Handlers
# =============================================================================


@router.callback_query(F.data == "admin:view_orders")
async def view_orders_start_handler(query: CallbackQuery, callback_message: Message):
    """
    Entry point for viewing orders. Displays the status filter keyboard.
    """
    keyboard = keyboards.get_admin_order_filters_keyboard()
    await callback_message.edit_text(
        "Please select a status to view orders:", reply_markup=keyboard
    )
    await query.answer()


@router.callback_query(F.data.startswith("admin_order_filter:"))
async def filter_orders_by_status_handler(
    query: CallbackQuery, session: AsyncSession, callback_message: Message
):
    """
    Handles a click on a status filter button. Fetches and displays
    a list of orders with the selected status.
    """
    if query.data is None:
        raise InvalidQueryDataError("Query data cannot be None")

    status_value = query.data.split(":")[1]
    status = OrderStatus(status_value)

    await callback_message.edit_text(
        f"Fetching {status.name.lower()} orders, please wait..."
    )

    orders = await order_service.get_orders_by_status_for_admin(session, status)

    text = f"<b>Orders - {status.name.capitalize()} ({len(orders)})</b>\n\n"
    if not orders:
        text += "No orders found with this status."

    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(
            text=f"{order.order_number} - {order.contact_name}"
            f" (${order.total_price:.2f})",
            callback_data=OrderCallbackFactory(action="view_details", item_id=order.id),
        )

    builder.button(text="⬅️ Back to Filters", callback_data="admin:view_orders")
    builder.adjust(1)

    await callback_message.edit_text(text, reply_markup=builder.as_markup())
    await query.answer()


@router.callback_query(OrderCallbackFactory.filter(F.action == "view_details"))  # type: ignore[arg-type]
async def admin_view_order_details_handler(
    query: CallbackQuery,
    callback_data: OrderCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """
    Displays the detailed view of a specific order for an admin.
    This reuses the same callback data as the user-facing order history.
    """
    order = None
    order_id = callback_data.item_id
    if order_id is not None:
        order = await crud.get_order(session, order_id)

    if not order:
        await query.answer("Could not find this order.", show_alert=True)
        return

    order_dto = OrderDTO.model_validate(order)
    await send_order_details_view(callback_message, order_dto)
    await query.answer()


@router.callback_query(F.data.startswith("admin_order_status:"))
async def change_order_status_handler(
    query: CallbackQuery,
    session: AsyncSession,
    callback_message: Message,
    bot: Bot,
):
    """
    Handles a click on a status change button.
    After a successful update, it notifies the customer.
    """
    if query.data is None:
        raise InvalidQueryDataError("Query data cannot be None")

    _, order_id_str, new_status_value = query.data.split(":")
    
    try:
        order_id = int(order_id_str)
    except ValueError:
        await query.answer("Invalid order ID format.", show_alert=True)
        return
        
    new_status = OrderStatus(new_status_value)

    try:
        updated_order_dto = await order_service.change_order_status(
            session, order_id, new_status
        )
        await query.answer(
            f"Order status updated to {new_status.name.capitalize()}", show_alert=True
        )
        await notification_service.send_order_status_update(bot, updated_order_dto)

        # Refresh the admin's detailed view
        await send_order_details_view(callback_message, updated_order_dto)

    except Exception as e:
        logger.error(
            f"Failed to change status for order {order_id}: {e}", exc_info=True
        )
        await query.answer(
            "An error occurred while updating the status.", show_alert=True
        )
        try:
            # Attempt to refresh the view even if status update failed
            order = await crud.get_order(session, order_id)
            if order:
                order_dto = OrderDTO.model_validate(order)
                await send_order_details_view(callback_message, order_dto)
        except Exception as refresh_e:
            logger.error(f"Failed to refresh order view for order {order_id}: {refresh_e}")
