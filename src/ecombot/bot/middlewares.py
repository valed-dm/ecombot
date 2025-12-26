"""
Defines custom middlewares for the bot.

Middlewares are used to process incoming updates before they reach the handlers.
This is the ideal place for tasks like managing database sessions, handling
authorization, or collecting metrics.
"""

from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

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
            async with session.begin():
                data["session"] = session
                return await handler(event, data)


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
    """

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

        return await handler(event, data)
