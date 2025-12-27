"""Main admin router that combines all admin handlers."""

from aiogram import Router

from ecombot.bot.filters.is_admin import IsAdmin
from ecombot.bot.middlewares import MessageInteractionMiddleware

# Import all handler modules
from . import categories, navigation, products

# Create main router
router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.callback_query.middleware(MessageInteractionMiddleware())

# Include all sub-routers
router.include_router(navigation.router)
router.include_router(categories.router)
router.include_router(products.router)