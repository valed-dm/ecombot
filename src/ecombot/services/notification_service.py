"""
Service layer for sending notifications to users.
"""

from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from ecombot.config import settings
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus


async def send_order_status_update(bot: Bot, order: OrderDTO):
    """
    Sends a notification to a user about a change in their order status.
    Uses HTML parse mode for robust formatting.
    """
    user_telegram_id = order.user.telegram_id
    text = ""
    safe_order_number = escape(order.display_order_number)

    # Get localized status name using common messages
    status_name = manager.get_message("common", order.status.message_key)

    if order.status == OrderStatus.PROCESSING:
        text = manager.get_message(
            "orders",
            "notification_processing",
            status=status_name,
            order_number=safe_order_number,
        )
    elif order.status == OrderStatus.PICKUP_READY:
        text = manager.get_message(
            "orders",
            "notification_pickup_ready",
            status=status_name,
            order_number=safe_order_number,
        )
        if order.pickup_point:
            text += f"\n\n📍 {escape(order.pickup_point.address)}"
            if order.pickup_point.working_hours:
                text += f"\n🕒 {escape(order.pickup_point.working_hours)}"
    elif order.status == OrderStatus.PAID:
        text = manager.get_message(
            "orders",
            "notification_paid",
            status=status_name,
            order_number=safe_order_number,
        )
    elif order.status == OrderStatus.SHIPPED:
        text = manager.get_message(
            "orders",
            "notification_shipped",
            status=status_name,
            order_number=safe_order_number,
        )
    elif order.status == OrderStatus.COMPLETED:
        text = manager.get_message(
            "orders", "notification_completed", order_number=safe_order_number
        )
    elif order.status == OrderStatus.CANCELLED:
        text = manager.get_message(
            "orders",
            "notification_cancelled",
            status=status_name,
            order_number=safe_order_number,
        )
    elif order.status == OrderStatus.REFUNDED:
        text = manager.get_message(
            "orders",
            "notification_refunded",
            status=status_name,
            order_number=safe_order_number,
        )
    elif order.status == OrderStatus.FAILED:
        text = manager.get_message(
            "orders",
            "notification_failed",
            status=status_name,
            order_number=safe_order_number,
        )

    if text:
        try:
            await bot.send_message(chat_id=user_telegram_id, text=text)
            log.info(
                f"Sent status update for order {order.order_number}"
                f" to user {user_telegram_id}"
            )
        except TelegramBadRequest as e:
            # If the user has blocked the bot
            log.warning(f"Failed to send notification to user {user_telegram_id}: {e}")
        except Exception as e:
            log.error(
                f"An unexpected error occurred sending notification to user"
                f" {user_telegram_id}: {e}",
                exc_info=True,
            )


async def notify_admins_new_order(bot: Bot, order: OrderDTO):
    """
    Notifies all admins about a new order.
    """
    safe_order_number = escape(order.display_order_number)
    safe_contact_name = escape(order.contact_name)

    text = manager.get_message(
        "orders",
        "admin_new_order",
        order_number=safe_order_number,
        contact_name=safe_contact_name,
        user_id=order.user.telegram_id,
        items_count=len(order.items),
        total=order.total_price,
    )

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=text)
        except Exception as e:
            log.error(f"Failed to notify admin {admin_id} about new order: {e}")
