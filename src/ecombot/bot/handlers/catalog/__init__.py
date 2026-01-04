"""
Catalog package - modular product catalog handlers.

This module contains handlers for navigating categories and viewing products.
"""

from aiogram import Router

from ecombot.bot.middlewares import MessageInteractionMiddleware

from . import navigation
from . import viewing


# Create main router and include all sub-routers
router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())

router.include_router(navigation.router)
router.include_router(viewing.router)

__all__ = ["router"]
