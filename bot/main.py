"""This module contains the main bot logic, including command handlers"""
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import bot.handlers.admin_commands as admin_commands
import bot.handlers.common_commands as common_commands
import bot.handlers.policies_commands as policies_commands
from bot.handlers import clients_manager, clients_commands
from bot.middlewares.db_middleware import DBSessionMiddleware
from bot.middlewares.is_admin_middleware import AdminMiddleware
from bot.middlewares.only_clients_middleware import OnlyClientsMiddleware
from bot.modules.logger import get_logger
from bot.modules.models import Base
from bot.modules.stat_extractor import setup_scheduler

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
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher(storage = MemoryStorage())
    dp.update.outer_middleware(DBSessionMiddleware(sessionmaker))
    dp.update.outer_middleware(OnlyClientsMiddleware(admin_id))
    dp.include_router(common_commands.router)
    dp.include_router(admin_commands.router)
    dp.include_router(clients_manager.router)
    dp.include_router(policies_commands.router)
    dp.include_router(clients_commands.router)
    common_commands.router.message.outer_middleware(AdminMiddleware(admin_id, True))
    admin_commands.router.message.outer_middleware(AdminMiddleware(admin_id, False))
    clients_manager.router.message.outer_middleware(AdminMiddleware(admin_id, False))

    if api_server:
        logger.info(f"Scheduler was set.")
        setup_scheduler(sessionmaker, api_server)

    await dp.start_polling(bot)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
