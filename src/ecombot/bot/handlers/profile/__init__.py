"""
Profile package - modular user profile and address management handlers.

This module contains handlers for the user profile and address management.
"""

from aiogram import Router

from ecombot.bot.middlewares import MessageInteractionMiddleware

from . import main_profile
from .main_profile import profile_handler
from . import address_management
from . import navigation
from .states import AddAddress
from .states import EditProfile


# Create main router and include all sub-routers
router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())

router.include_router(main_profile.router)
router.include_router(address_management.router)
router.include_router(navigation.router)

__all__ = ["router", "EditProfile", "AddAddress", "profile_handler"]
