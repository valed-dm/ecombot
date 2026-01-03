"""Product management handlers package."""

from aiogram import Router

from . import add
from . import delete
from . import edit


router = Router()
router.include_router(add.router)
router.include_router(edit.router)
router.include_router(delete.router)
