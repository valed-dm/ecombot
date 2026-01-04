"""
Cart package - modular shopping cart handlers.

This module contains handlers for adding items to the cart, viewing the cart,
and managing cart item quantities.
"""

from aiogram import Router

from ecombot.bot.middlewares import MessageInteractionMiddleware

from . import item_management
from . import viewing


# Create main router and include all sub-routers
router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())

router.include_router(viewing.router)
router.include_router(item_management.router)

__all__ = ["router"]
