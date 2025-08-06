from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class IsAdminMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int):
        self.__admin_id = admin_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        data["is_admin"] = False
        if user is not None:
            data["is_admin"] = (user.id == self.__admin_id)
        return await handler(event, data)
