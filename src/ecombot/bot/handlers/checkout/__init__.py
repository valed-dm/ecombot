"""
Checkout package - modular checkout process handlers.

This package contains the FSM and handlers to guide the user through
collecting their contact information and confirming their order. It features
a "fast path" for returning users with complete profiles and a "slow path"
for first-time users, which then saves their details for future use.
"""

from aiogram import Router

from . import fast_path
from . import main
from . import slow_path
from .states import CheckoutFSM


# Create main router and include all sub-routers
router = Router()
router.include_router(main.router)
router.include_router(fast_path.router)
router.include_router(slow_path.router)

__all__ = ["router", "CheckoutFSM"]
