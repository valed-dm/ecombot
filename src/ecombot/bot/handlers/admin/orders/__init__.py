"""
Admin Orders package - modular order management handlers.

This module contains the handlers for the admin workflow of viewing,
filtering, and updating the status of customer orders.
"""

from aiogram import Router

from . import navigation
from . import status_management
from . import viewing


# Create main router and include all sub-routers
router = Router()

router.include_router(navigation.router)
router.include_router(viewing.router)
router.include_router(status_management.router)

__all__ = ["router"]
