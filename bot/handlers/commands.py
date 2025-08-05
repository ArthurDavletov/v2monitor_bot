import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold, Pre
from dotenv import load_dotenv

from bot.modules.logger import get_logger
from bot.modules.v2ray import is_service_active, get_stats
from bot.keyboards.menu_keyboard import create_main_menu, settings_menu

logger = get_logger(__name__)

router = Router()

load_dotenv()
API_SERVER = os.getenv("API_SERVER")


@router.message(CommandStart())
async def command_start_handler(message: Message, is_admin: bool, is_client: bool) -> None:
    """This handler receives messages with `/start` command"""
    logger.info(f"Received /start command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin}, user = {is_client})")
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name),
        "\n"
    )
    if not is_admin and not is_client:
        content += Text("You're not authorized to use this bot. Please contact an administrator.")
    if is_admin and not is_client:
        content += Text("You're an admin, but there's no email (your ID in v2ray) in the database")
    if not is_admin and is_client:
        content += Text("You're the client! Congratulations!")
    if is_admin and is_client:
        content += Text("You're an admin and can use client's commands!")
    await message.answer(**content.as_kwargs(), reply_markup=create_main_menu(is_admin, True, True, True))


@router.message(F.text == "Status 🛠")
async def command_status_handler(message: Message, is_admin: bool, is_client: bool) -> None:
    """This handler receives messages with `Status 🛠` command"""
    logger.info(f"Received `Status 🛠` command from {message.from_user.full_name}"
                f"(ID: {message.from_user.id}, admin = {is_admin}, user = {is_client})")
    if not is_admin:
        text = "You're not an admin, you can't use this command."
        await message.answer(text)
        return
    text = ""
    for service in ("v2ray", "nginx"):
        if is_service_active(service):
            text += f"The {service} service is currently active. ✅\n"
        else:
            text += f"The {service} service isn't active. ❌\n"
    await message.answer(text)


@router.message(F.text == "All Stats 📊")
async def command_stats_handler(message: Message, is_admin: bool, is_client: bool) -> None:
    """This handler receives messages with `All Stats 📊` command"""
    logger.info(f"Received `All Stats 📊` command from {message.from_user.full_name}"
                f"(ID: {message.from_user.id}, admin = {is_admin}, user = {is_client})")
    if not is_admin:
        text = "You're not an admin, you can't use this command."
        await message.answer(text)
        return
    text = get_stats(API_SERVER)
    content = Text(Pre(text))
    await message.answer(**content.as_kwargs())


@router.message(F.text == "Settings ⚙️")
async def command_settings_handler(message: Message, is_admin: bool, is_client: bool) -> None:
    """This handler receives messages with `Settings ⚙️` command"""
    logger.info(f"Received `Settings ⚙️` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin}, user = {is_client})")
    await message.answer("Settings menu:", reply_markup=settings_menu(is_admin))


@router.message(F.text == "Back to Main Menu ↩️")
async def command_back_to_main_menu_handler(message: Message, is_admin: bool, is_client: bool) -> None:
    """This handler receives messages with `Back to Main Menu ↩️` command"""
    logger.info(f"Received `Back to Main Menu ↩️` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin}, user = {is_client})")
    await message.answer("Main menu:", reply_markup=create_main_menu(is_admin, True, True, True))
