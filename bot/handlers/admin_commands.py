import os

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import Text, Pre
from dotenv import load_dotenv

from bot.modules.logger import get_logger
from bot.modules.v2ray import is_service_active, get_stats

logger = get_logger(__name__)

router = Router()

load_dotenv()
API_SERVER = os.getenv("API_SERVER")


@router.message(F.text == "Status 🛠")
async def command_status_handler(message: Message) -> None:
    """This handler receives messages with `Status 🛠` command"""
    logger.info(f"Received `Status 🛠` command from {message.from_user.full_name}"
                f"(ID: {message.from_user.id})")
    text = ""
    for service in ("v2ray", "nginx"):
        if is_service_active(service):
            text += f"The {service} service is currently active. ✅\n"
        else:
            text += f"The {service} service isn't active. ❌\n"
    await message.answer(text)


@router.message(F.text == "All Stats 📊")
async def command_stats_handler(message: Message) -> None:
    """This handler receives messages with `All Stats 📊` command"""
    logger.info(f"Received `All Stats 📊` command from {message.from_user.full_name}"
                f"(ID: {message.from_user.id})")
    text = get_stats(API_SERVER)
    content = Text(Pre(text))
    await message.answer(**content.as_kwargs())

