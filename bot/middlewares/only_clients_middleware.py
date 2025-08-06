from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select

from bot.modules.models import Client


class OnlyClientsMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int):
        self.__admin_id = admin_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        if user is None:
            return None
        if user.id == self.__admin_id:
            return await handler(event, data)
        async with data["sessionmaker"]() as session:
            result = await session.execute(select(Client).where(Client.id == user.id))
            if result.scalar() is None:
                await event.message.answer("You aren't authorized to use this bot. Contact your administrator.")
                return None
            return await handler(event, data)
