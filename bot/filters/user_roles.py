from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.modules.models import Client


class IsAdmin(Filter):
    """Filter to check if the user is an admin."""
    def __init__(self, admin_id: int):
        super().__init__()
        self.__admin_id = admin_id

    async def __call__(self, message: Message) -> bool:
        """Check if the message sender is the admin."""
        if self.__admin_id is None:
            return False
        return message.from_user.id == self.__admin_id


class IsClient(Filter):
    """Filter to check if the user is a client."""
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def __call__(self, message: Message) -> bool:
        """Check if the message sender is client."""
        user = await self.session.get(Client, message.from_user.id)
        return user is not None
