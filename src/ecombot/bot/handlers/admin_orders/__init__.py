"""
Admin Orders package - modular order management handlers.

This module contains the handlers for the admin workflow of viewing,
filtering, and updating the status of customer orders.
"""

from aiogram import Router

from ecombot.bot.filters.is_admin import IsAdmin
from ecombot.bot.middlewares import MessageInteractionMiddleware

from . import navigation
from . import status_management
from . import viewing


# Create main router and include all sub-routers
router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.callback_query.middleware(MessageInteractionMiddleware())

router.include_router(navigation.router)
router.include_router(viewing.router)
router.include_router(status_management.router)

__all__ = ["router"]
