import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties

from ecombot.bot.handlers import admin
from ecombot.bot.handlers import cart
from ecombot.bot.handlers import catalog
from ecombot.bot.handlers import checkout
from ecombot.bot.handlers import orders
from ecombot.bot.handlers import profile
from ecombot.bot.middlewares import DbSessionMiddleware
from ecombot.bot.middlewares import UserMiddleware
from ecombot.config import settings
from ecombot.db.database import AsyncSessionLocal
from ecombot.logging_setup import log


bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()

dp.update.middleware(DbSessionMiddleware(session_pool=AsyncSessionLocal))
dp.update.middleware(UserMiddleware())

dp.include_router(admin.router)
dp.include_router(catalog.router)
dp.include_router(cart.router)
dp.include_router(checkout.router)
dp.include_router(profile.router)
dp.include_router(orders.router)


async def main() -> None:
    """Run bot in polling mode."""
    log.info("Bot is starting in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log.error(f"Bot startup failed: {e}")
        raise
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
