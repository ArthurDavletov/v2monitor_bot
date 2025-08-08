import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Pre, Code, Strikethrough, as_marked_list
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.client_add_keyboard import client_manager_keyboard, confirm_keyboard
from bot.modules.logger import get_logger
from bot.modules.models import Client, ClientsTempSelection, ClientHistory, ClientTraffic, ClientRequests

logger = get_logger(__name__)

router = Router()


class ClientsManager(StatesGroup):
    add_client = State()
    remove_client = State()
    edit_client = State()


@router.message(F.text == "Manage Clients 👥")
async def command_manage_clients_handler(message: Message, session: AsyncSession) -> None:
    """This handler receives messages with `Manage Clients 👥` command"""
    logger.info(f"Received `Manage Clients 👥` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    users = (await session.scalars(select(Client))).all()
    await session.execute(delete(ClientsTempSelection).where(ClientsTempSelection.admin_id == message.from_user.id))
    await session.commit()
    if not users:
        content = Text("There are no clients registered in this server.")
    else:
        content = Text("List of registered clients:\n\n")
    for index, client in enumerate(users, start = 1):
        content += Text(f"{index}. {client.email} (ID: {client.id})\n")
        session.add(ClientsTempSelection(
            admin_id = message.from_user.id,
            client_id = client.id,
            number = index
        ))
    await session.commit()
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
    logger.info(f"Received `Add Client` command from {callback_query.from_user.full_name} "
                f"(ID: {callback_query.from_user.id})")
    await callback_query.answer()
    content = Text("Enter email (ID in v2ray) and Telegram ID of the new client.\n",
                   "Example: ", Pre("Friend 1234567890"), "\n",
                   "Write /cancel to cancel.")
    await callback_query.message.answer(**content.as_kwargs())
    await state.set_state(ClientsManager.add_client)


@router.message(ClientsManager.add_client)
async def final_add_client_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"Admin {message.from_user.full_name} (ID: {message.from_user.id}) wants to add new clients")
    text = message.text
    new_clients = {}
    for line in text.splitlines():
        last_space = line.rfind(" ")
        if last_space != -1:
            email, user_id = line[:last_space], line[last_space + 1:]
            if user_id.isdigit():
                new_clients[email] = user_id
    if len(new_clients) == 0:
        content = Text("There are no valid clients to register.")
    else:
        content = Text("Do you want to add this list of the clients to the database?\n\n")
    content += as_marked_list(*(f"{email} (ID: {user_id})" for email, user_id in new_clients.items()), marker = "❔ ")
    # for email, user_id in new_clients.items():
    #     content += Text("❔ ", email, " (ID: ", user_id, ")\n")
    await state.clear()
    await state.set_data(new_clients)
    await message.answer(**content.as_kwargs(), reply_markup = confirm_keyboard("add"))


@router.callback_query(F.data == "confirm_add_clients")
async def confirm_add_clients_handler(callback_query: CallbackQuery, state: FSMContext,
                                      session: AsyncSession) -> None:
    logger.info(f"Received `Confirm Add Clients` command from {callback_query.from_user.full_name} "
                f"(ID: {callback_query.from_user.id})")
    clients = await state.get_data()
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
async def remove_client_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"Received `Remove Client` command from {callback_query.from_user.full_name} "
                f"(ID: {callback_query.from_user.id})")
    await callback_query.answer()
    content = Text("Enter indexes of users, which do you want to remove\n",
                   "Example: ", Code("1"), " or ", Code("2-3"), " or ",
                   Code("1,2"), " or ", Code("1, 4"), "\n",
                   "Write /cancel to cancel.")
    await callback_query.message.answer(**content.as_kwargs())
    await state.set_state(ClientsManager.remove_client)


@router.message(ClientsManager.remove_client)
async def final_remove_client_handler(message: Message, state: FSMContext,
                                      session: AsyncSession) -> None:
    logger.info(f"Received `Final Remove Clients` command from {message.from_user.full_name} "
                f"(ID: {message.from_user.id})")
    indexes = set()
    text = message.text
    for number_match in re.split(r",\s*", text):
        if number_match.isdigit():
            indexes.add(int(number_match))
        match = re.match(r"(\d+)[-—–−-](\d+)", number_match)
        if match is None:
            continue
        start, end = map(int, match.groups())
        for i in range(start, end + 1):
            indexes.add(i)
    content = Text("Do you want to remove these clients from the database?\n\n")
    selected_clients = (await session.scalars(select(ClientsTempSelection).where(
        ClientsTempSelection.admin_id == message.from_user.id)
    )).all()
    remove_clients = []
    for client_selected in selected_clients:
        user_id, index = client_selected.client_id, client_selected.number
        if index in indexes:
            client = (await session.get(Client, user_id))
            remove_clients.append(user_id)
            content += Text(Strikethrough("❌ ", client.email, " (ID: ", user_id, ")"), "\n")
    await state.clear()
    if not remove_clients:
        await message.answer("There are no clients to remove from the database.")
        return
    await state.set_data({'remove_clients': remove_clients})
    await message.answer(**content.as_kwargs(), reply_markup = confirm_keyboard("remove"))


@router.callback_query(F.data == "confirm_remove_clients")
async def confirm_remove_clients_handler(callback_query: CallbackQuery, state: FSMContext,
                                         session: AsyncSession) -> None:
    logger.info(f"Admin {callback_query.from_user.full_name} (ID: {callback_query.from_user.id}) "
                f"deleted clients")
    user_ids = (await state.get_data())["remove_clients"]
    await session.execute(delete(Client).where(Client.id.in_(user_ids)))
    await session.execute(delete(ClientHistory).where(ClientHistory.user_id.in_(user_ids)))
    await session.execute(delete(ClientTraffic).where(ClientTraffic.user_id.in_(user_ids)))
    await session.execute(delete(ClientRequests).where(ClientRequests.user_id.in_(user_ids)))
    await session.commit()
    await callback_query.answer()
    if len(user_ids) == 1:
        content = Text("One client has been removed from the database:\n\n")
    else:
        content = Text("There are some clients have been removed from the database:\n\n")
    for user_id in user_ids:
        content += Text("❌ ID: ", user_id, "\n")
    await callback_query.message.edit_text(**content.as_kwargs())
    await state.clear()
