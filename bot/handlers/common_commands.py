from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.policies_commands import get_policies
from bot.keyboards.menu_keyboard import create_main_menu, settings_menu
from bot.modules.logger import get_logger
from bot.modules.models import Client

logger = get_logger(__name__)

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, is_admin: bool,
                                session: AsyncSession) -> None:
    """This handler receives messages with `/start` command"""
    logger.info(f"Received /start command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin})")
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name),
        "\n"
    )
    is_client = True
    result = await session.execute(select(Client).where(Client.id == message.from_user.id))
    if result.scalar() is None:
        is_client = False
    if is_admin and not is_client:
        content += Text("You're an admin, but there's no email (your ID in v2ray) in the database. "
                        "Add yourself via Settings -> Manage Clients")
    if not is_admin and is_client:
        content += Text("You're the client! Congratulations!")
    if is_admin and is_client:
        content += Text("You're an admin and can use the client's commands!")
    policies = await get_policies(message.from_user.id, session)
    await message.answer(
        **content.as_kwargs(),
        reply_markup=create_main_menu(is_admin, *policies)
    )


@router.message(F.text == "Settings ⚙️")
async def command_settings_handler(message: Message, is_admin: bool) -> None:
    """This handler receives messages with `Settings ⚙️` command"""
    logger.info(f"Received `Settings ⚙️` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin})")
    await message.answer("Settings menu:", reply_markup=settings_menu(is_admin))


@router.message(F.text == "Back to Main Menu ↩️")
async def command_back_to_main_menu_handler(message: Message, is_admin: bool,
                                            session: AsyncSession) -> None:
    """This handler receives messages with `Back to Main Menu ↩️` command"""
    logger.info(f"Received `Back to Main Menu ↩️` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id}, admin = {is_admin})")
    policies = await get_policies(message.from_user.id, session)
    await message.answer(
        "Main menu:",
        reply_markup=create_main_menu(is_admin, *policies)
    )
