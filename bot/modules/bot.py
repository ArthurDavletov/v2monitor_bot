"""This module contains the main bot logic, including command handlers"""
import os
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold, Pre

from modules.logger import get_logger
from modules.v2ray import is_service_active, get_stats


load_dotenv()
logger = get_logger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
API_SERVER = os.getenv("API_SERVER")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    raise ValueError("BOT_TOKEN is required to run the bot.")
if not ADMIN_ID:
    logger.warning("ADMIN_ID is not set in the environment variables. Bot won't answer admin commands.")
if not API_SERVER:
    logger.warning("API_SERVER is not set in the environment variables! Stats may not work correctly.")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    logger.error(f"Invalid ADMIN_ID: {ADMIN_ID}. It should be an integer.")
    ADMIN_ID = None


class IsAdmin(Filter):
    """Filter to check if the user is an admin."""
    def __init__(self, admin_id: int):
        super().__init__()
        self.admin_id = admin_id

    async def __call__(self, message: Message) -> bool:
        """Check if the message sender is the admin."""
        if self.admin_id is None:
            return False
        return message.from_user.id == self.admin_id


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


del BOT_TOKEN


@dp.message(CommandStart(), IsAdmin(ADMIN_ID))
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command"""
    logger.info(f"Received /start command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = True)")
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name),
        "\nYou are an admin, so you can use all commands."
    )
    await message.answer(**content.as_kwargs())


@dp.message(CommandStart())
async def command_start_public_handler(message: Message) -> None:
    """This handler receives messages with `/start` command from non-admin users"""
    logger.info(f"Received /start command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = False)")
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name),
        "\nYou are not an admin, but you can still use some commands."
    )
    await message.answer(**content.as_kwargs())


@dp.message(Command("status"), IsAdmin(ADMIN_ID))
async def command_status_handler(message: Message) -> None:
    """This handler receives messages with `/status` command"""
    logger.info(f"Received /status command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = True)")
    text = ""
    for service in ("v2ray", "nginx"):
        if is_service_active(service):
            text += f"The {service} service is currently active. ✅\n"
        else:
            text += f"The {service} service isn't active. ❌\n"
    await message.answer(text)


@dp.message(Command("status"))
async def command_status_public_handler(message: Message) -> None:
    """This handler receives messages with `/status` command from non-admin users"""
    logger.info(f"Received /status command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = False)")
    text = "You're not an admin, so I can't provide detailed status information. 😔"
    await message.answer(text)


@dp.message(Command("stats"), IsAdmin(ADMIN_ID))
async def command_stats_handler(message: Message) -> None:
    """This handler receives messages with `/stats` command"""
    logger.info(f"Received /stats command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = True)")
    text = get_stats(API_SERVER)
    content = Text(Pre(text))
    await message.answer(**content.as_kwargs())


@dp.message(Command("stats"))
async def command_stats_public_handler(message: Message) -> None:
    """This handler receives messages with `/stats` command from non-admin users"""
    logger.info(f"Received /stats command from {message.from_user.full_name} (ID: {message.from_user.id}, admin = False)")
    text = "You're not an admin, so I can't provide detailed stats. 😔"
    await message.answer(text)


async def main() -> None:
    """Main function to start the bot."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
