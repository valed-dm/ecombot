"""
Checkout package - modular checkout process handlers.

This package contains the FSM and handlers to guide the user through
collecting their contact information and confirming their order. It features
a "fast path" for returning users with complete profiles and a "slow path"
for first-time users, which then saves their details for future use.
"""

from aiogram import Router

from .fast_path import router as fast_path_router
from .main import router as main_router
from .slow_path import router as slow_path_router


router = Router()

router.include_router(main_router)
router.include_router(fast_path_router)
router.include_router(slow_path_router)
