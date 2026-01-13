import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from fastapi import FastAPI
from fastapi import Request

from ecombot.bot.handlers import admin
from ecombot.bot.handlers import admin_orders
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


# Initialize Bot and Dispatcher globally for Vercel/FastAPI
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()

# Register middlewares
dp.update.middleware(DbSessionMiddleware(session_pool=AsyncSessionLocal))
dp.update.middleware(UserMiddleware())

# Include routers
dp.include_router(admin.router)
dp.include_router(admin_orders.router)
dp.include_router(catalog.router)
dp.include_router(cart.router)
dp.include_router(checkout.router)
dp.include_router(profile.router)
dp.include_router(orders.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI (startup/shutdown)."""
    if settings.WEBHOOK_URL:
        webhook_url = f"{settings.WEBHOOK_URL}/webhook"
        log.info(f"Setting webhook to {webhook_url}")
        await bot.set_webhook(webhook_url)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming Telegram updates via webhook."""
    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        log.error(f"Webhook error: {e}")
        return {"status": "error"}


async def main() -> None:
    """Run polling for local development."""
    log.info("Bot is starting...")
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
