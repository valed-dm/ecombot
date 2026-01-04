"""
Orders package - modular order history handlers.

This module contains handlers for viewing user order history and details.
"""

from aiogram import Router

from ecombot.bot.middlewares import MessageInteractionMiddleware

from . import details
from . import listing


# Create main router and include all sub-routers
router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())

router.include_router(listing.router)
router.include_router(details.router)

__all__ = ["router"]
