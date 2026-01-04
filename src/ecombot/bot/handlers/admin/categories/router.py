"""Category management router."""

from aiogram import Router

from .add import router as add_router
from .delete import router as delete_router
from .restore import router as restore_router


router = Router()
router.include_routers(add_router, delete_router, restore_router)
