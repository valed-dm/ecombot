from aiogram import Router

from . import delivery_types
from . import menu
from . import pickup_points


router = Router()

router.include_routers(menu.router, pickup_points.router, delivery_types.router)
