"""This module contains the main bot logic, including command handlers"""
import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold, Pre
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from bot.modules.models import Base
from bot.modules.logger import get_logger
from bot.modules.v2ray import is_service_active, get_stats
from bot.filters.user_roles import IsAdmin, IsClient
from middlewares.roles import RolesMiddleware
import handlers.commands as commands


logger = get_logger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")
    api_server = os.getenv("API_SERVER")
    database_url = os.getenv("DATABASE_URL")

    if not bot_token:
        logger.error("BOT_TOKEN is not set in the environment variables.")
        raise ValueError("BOT_TOKEN is required to run the bot.")
    if not admin_id:
        logger.warning("ADMIN_ID is not set in the environment variables. Bot won't answer admin commands.")
    if not api_server:
        logger.warning("API_SERVER is not set in the environment variables! Stats may not work correctly.")
    if not database_url:
        logger.warning("DATABASE_URL is not set in the environment variables. Stats may not work correctly.")

    try:
        admin_id = int(admin_id)
    except ValueError:
        logger.error(f"Invalid ADMIN_ID: {admin_id}. It should be an integer.")
        admin_id = None

    bot = Bot(
        token = bot_token,
        default = DefaultBotProperties(parse_mode = ParseMode.HTML)
    )

    del bot_token

    engine = create_async_engine(database_url)
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher()
    dp.include_router(commands.router)
    commands.router.message.middleware(RolesMiddleware(admin_id, async_session))
    await dp.start_polling(bot)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
