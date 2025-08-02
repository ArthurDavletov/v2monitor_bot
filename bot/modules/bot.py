import os
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from modules.logger import get_logger


load_dotenv()
logger = get_logger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    raise ValueError("BOT_TOKEN is required to run the bot.")
if not ADMIN_ID:
    logger.error("ADMIN_ID is not set in the environment variables.")
    raise ValueError("ADMIN_ID is required to run the bot.")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

del BOT_TOKEN, ADMIN_ID


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command"""
    logger.info(f"Received /start command from {message.from_user.full_name} (ID: {message.from_user.id})")
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
