from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.modules.models import Client


class RolesMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int, session: async_sessionmaker[AsyncSession]):
        self.__admin_id = admin_id
        self.__session = session

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        data["is_admin"] = data["is_client"] = False
        if user is not None:
            data["is_admin"] = (user.id == self.__admin_id)
            async with self.__session() as session:
                result = await session.execute(select(Client).where(Client.id == user.id))
                data["is_client"] = result.scalar() is not None
        return await handler(event, data)
