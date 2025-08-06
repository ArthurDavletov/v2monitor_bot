import os
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Pre, Code, Strikethrough
from dotenv import load_dotenv
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.keyboards.client_add_keyboard import client_manager_keyboard, confirm_keyboard
from bot.modules.logger import get_logger
from bot.modules.models import Client, ClientsTempSelection, ClientHistory, ClientTraffic, ClientRequests
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


class ClientsManager(StatesGroup):
    add_client = State()
    remove_client = State()
    edit_client = State()


@router.message(F.text == "Manage Clients 👥")
async def command_manage_clients_handler(message: Message, sessionmaker: async_sessionmaker[AsyncSession],
                                         state: FSMContext) -> None:
    """This handler receives messages with `Manage Clients 👥` command"""
    logger.info(f"Received `Manage Clients 👥` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    async with sessionmaker() as session:
        users = (await session.scalars(select(Client))).all()
        await session.execute(delete(ClientsTempSelection).where(ClientsTempSelection.user_id == message.from_user.id))
        await session.commit()
    if not users:
        content = Text("There are no clients registered in this server.")
    else:
        content = Text("List of registered clients:\n\n")
    for index, client in enumerate(users, start = 1):
        content += Text(index, ") ", client.email, " (ID: ", client.id, ")\n")
    await state.set_data({"clients": users})
    await message.answer(**content.as_kwargs(), reply_markup = client_manager_keyboard(len(users) != 0))


@router.message(Command(commands=["cancel"]))
async def command_cancel(message: Message, state: FSMContext) -> None:
    await message.answer("Cancelled.")
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer(text="Cancelled.")
    await state.clear()
    await callback_query.message.delete()


@router.callback_query(F.data == "add_client")
async def add_client_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    content = Text("Enter email (ID in v2ray) and Telegram ID of the new client.\n",
                   "Example: ", Pre("Friend 1234567890"), "\n",
                   "Write /cancel to cancel.")
    await callback_query.message.answer(**content.as_kwargs())
    await state.set_state(ClientsManager.add_client)


@router.message(ClientsManager.add_client)
async def final_add_client_handler(message: Message, state: FSMContext) -> None:
    text = message.text
    new_clients = {}
    for line in text.splitlines():
        last_space = text.rfind(" ")
        if last_space != -1:
            email, user_id = text[:last_space], text[last_space + 1:]
            if user_id.isdigit():
                new_clients[email] = user_id
    if len(new_clients) == 0:
        content = Text("There are no valid clients to register.")
    else:
        content = Text("Do you want to add this list of the clients to the database?\n\n")
    for email, user_id in new_clients.items():
        content += Text("❔ ", email, " (ID: ", user_id, ")\n")
    await state.clear()
    await state.set_data(new_clients)
    await message.answer(**content.as_kwargs(), reply_markup = confirm_keyboard("add"))


@router.callback_query(F.data == "confirm_add_clients")
async def confirm_add_clients_handler(callback_query: CallbackQuery, state: FSMContext,
                                      sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    clients = await state.get_data()
    async with sessionmaker() as session:
        for email, user_id in clients.items():
            session.add(Client(
                id = user_id,
                email = email
            ))
        await session.commit()
    await callback_query.answer()
    if len(clients) == 1:
        content = Text("There is one client added to this database:\n\n")
    else:
        content = Text("There are some clients added to this database:\n\n")
    for email, user_id in clients.items():
        content += Text("✅ ", email, " (ID: ", user_id, ")\n")
    await callback_query.message.edit_text(**content.as_kwargs())
    await state.clear()


@router.callback_query(F.data == "remove_client")
async def remove_client_handler(callback_query: CallbackQuery, state: FSMContext,
                                sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    await callback_query.answer()
    content = Text("Enter indexes of users, which do you want to remove\n",
                   "Example: ", Code("1"), " or ", Code("2-3"), " or ",
                   Code("1,2"), " or ", Code("1, 4"), "\n",
                   "Write /cancel to cancel.")
    await callback_query.message.answer(**content.as_kwargs())
    await state.set_state(ClientsManager.remove_client)


@router.message(ClientsManager.remove_client)
async def final_remove_client_handler(message: Message, state: FSMContext) -> None:
    indexes = set()
    text = message.text
    for number_match in re.split(r",\s*", text):
        if number_match.isdigit():
            indexes.add(int(number_match))
        match = re.match(r"(\d+)[-—–−-](\d+)", number_match)
        if match is None:
            continue
        start, end = match.groups()
        for i in range(start, end + 1):
            indexes.add(i)
    if len(indexes) == 0:
        content = Text("There are no clients to remove.")
    else:
        content = Text("Do you want to remove these clients to the database?\n\n")
    clients = (await state.get_data())["clients"]  # it isn't good I know
    remove_clients = []
    for index, (email, user_id) in enumerate(clients.items(), start=1):
        if index in indexes:
            remove_clients.append(user_id)
            content += Text(Strikethrough("❌ ", email, " (ID: ", user_id, ")"), "\n")
        else:
            content += Text("⚪ ", email, " (ID: ", user_id, ")\n")
    await state.clear()
    await state.set_data({'remove_clients': remove_clients})
    await message.answer(**content.as_kwargs(), reply_markup = confirm_keyboard("remove"))


@router.callback_query(F.data == "confirm_remove_clients")
async def confirm_remove_clients_handler(callback_query: CallbackQuery, state: FSMContext,
                                         sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    user_ids = (await state.get_data())["remove_clients"]
    with sessionmaker() as session:
        session.execute(delete(Client).where(Client.id.in_(user_ids)))
        session.execute(delete(ClientHistory).where(ClientHistory.user_id.in_(user_ids)))
        session.execute(delete(ClientTraffic).where(ClientTraffic.user_id.in_(user_ids)))
        session.execute(delete(ClientRequests).where(ClientRequests.user_id.in_(user_ids)))
        session.commit()
    await callback_query.answer()
    if len(user_ids) == 1:
        content = Text("One client has been removed from the database:\n\n")
    else:
        content = Text("There are some clients have been removed from the database:\n\n")
    for user_id in user_ids:
        content += Text("❌ ID: ", user_id, ")\n")
    await callback_query.message.edit_text(**content.as_kwargs())
    await state.clear()
