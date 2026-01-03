"""
Defines custom middlewares for the bot.

Middlewares are used to process incoming updates before they reach the handlers.
This is the ideal place for tasks like managing database sessions, handling
authorization, or collecting metrics.
"""

import contextlib
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict

from aiogram import BaseMiddleware
from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from ecombot.config import settings
from ecombot.db import crud
from ecombot.db.models import User


class DbSessionMiddleware(BaseMiddleware):
    """
    This middleware creates a new SQLAlchemy session for each update and
    injects it into the handler's keyword arguments.
    """

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        # Store the session pool from the main application
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        This method is called for each update.
        """
        async with self.session_pool() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise


class MessageInteractionMiddleware(BaseMiddleware):
    """
    This middleware checks that a CallbackQuery has a valid, accessible
    Message object attached. It prevents handlers from crashing on stale
    callbacks from deleted or inaccessible messages.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        if isinstance(event.message, Message):
            data["callback_message"] = event.message
            return await handler(event, data)

        await event.answer(
            "This action is no longer available or the message has changed.",
            show_alert=True,
        )
        return None


class UserMiddleware(BaseMiddleware):
    """
    This middleware fetches or creates a user record from the database for
    every update from a user and injects it into the handler's context.
    Also sets role-based bot commands automatically.
    """

    def __init__(self):
        self._user_commands_cache = {}  # Track user_id -> is_admin status

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        telegram_user = data.get("event_from_user")
        if not telegram_user:
            return await handler(event, data)

        session: AsyncSession | None = data.get("session")
        if not session:
            # If session is not available, skip user middleware
            return await handler(event, data)

        db_user: User = await crud.get_or_create_user(session, telegram_user)

        # Inject the user object into the context
        data["db_user"] = db_user

        # Check if commands need updating
        current_admin_status = telegram_user.id in settings.ADMIN_IDS
        cached_status = self._user_commands_cache.get(telegram_user.id)

        if cached_status != current_admin_status:
            bot: Bot = data.get("bot")
            if bot:
                await self._set_user_commands(bot, telegram_user.id)
                self._user_commands_cache[telegram_user.id] = current_admin_status

        return await handler(event, data)

    async def _set_user_commands(self, bot: Bot, user_id: int) -> None:
        """Set role-based commands for the user."""
        common_commands = [
            BotCommand(command="start", description="🛍️ Browse catalog"),
            BotCommand(command="cart", description="🛒 View shopping cart"),
            BotCommand(command="orders", description="📦 Order history"),
            BotCommand(command="profile", description="👤 Manage profile"),
        ]

        admin_commands = [
            BotCommand(command="admin", description="⚙️ Admin panel"),
            BotCommand(command="cancel", description="❌ Cancel operation"),
        ]

        is_admin = user_id in settings.ADMIN_IDS
        commands = common_commands + (admin_commands if is_admin else [])

        with contextlib.suppress(Exception):
            await bot.set_my_commands(
                commands, scope={"type": "chat", "chat_id": user_id}
            )
