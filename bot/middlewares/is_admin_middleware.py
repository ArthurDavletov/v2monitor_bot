from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int, allow_clients: bool = False) -> None:
        self.__admin_id = admin_id
        self.__allow_clients = allow_clients

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        is_admin = (user.id == self.__admin_id)
        if self.__allow_clients:
            data["is_admin"] = is_admin
            return await handler(event, data)
        if is_admin:
            return await handler(event, data)
        await event.message.answer("You're not an admin. You can't use the admin's commands!")
        return None

