from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.modules.logger import get_logger
from bot.modules.models import Client

logger = get_logger(__name__)

router = Router()


@router.message(F.text == "Traffic 📈")
async def traffic_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `Traffic` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    access = (await session.get(Client, message.from_user.id)).traffic_access
    if not access:
        await message.answer("You don't granted access to the traffic in /policy")
        return
    await message.answer("Not implemented yet :)")


@router.message(F.text == "History 📜")
async def history_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `History` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    access = (await session.get(Client, message.from_user.id)).history_access
    if not access:
        await message.answer("You don't granted access to the history in /policy")
        return
    await message.answer("Not implemented yet :))")


@router.message(F.text == "Requests's count 📈")
async def requests_handler(message: Message, session: AsyncSession) -> None:
    logger.info(f"Received `Requests's count` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    access = (await session.get(Client, message.from_user.id)).requests_access
    if not access:
        await message.answer("You don't granted access to the requests in /policy")
        return
    await message.answer("Not implemented yet :)))")
