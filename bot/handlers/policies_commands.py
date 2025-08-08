from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, as_line, Underline
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.policy_keyboard import create_policy_keyboard, PolicyAccess
from bot.modules.logger import get_logger
from bot.modules.models import Client


async def get_policies(user_id: int, session: AsyncSession) -> tuple[bool, bool, bool]:
    client = (await session.scalars(select(Client).where(Client.id == user_id))).first()
    if client is None:
        return False, False, False
    return client.traffic_access, client.history_access, client.requests_access


logger = get_logger(__name__)

router = Router()


@router.message(Command(commands=["policy"]))
@router.message(F.text == "Change Policy 📜")
async def change_policy_handler(message: Message, session: AsyncSession,
                                state: FSMContext) -> None:
    logger.info(f"Received `Change Policy` command from {message.from_user.full_name} "
                f"ID: {message.from_user.id}")
    content = Text("This bot provides several useful features:\n")
    content += Text("1. ") + Underline("Traffic") + Text(" usage analysis.\n")
    content += (Text("2. Tracking of ") + Underline("visited domains") +
                Text(" and ") + Underline("IP addresses") +
                Text(" (for example, example.com or 23.215.0.138). "
                     "It is important to note that your data and the contents of the pages remain confidential.\n"))
    content += Text("3. Real-time ") + Underline("request counting") + Text(" usage analysis.\n\n")
    content += as_line(
        "You can choose which functions to activate."
        "If you do not check the necessary options, the bot will not collect information.")
    content += Text("To use these functions, check the appropriate boxes.")
    policies = await get_policies(user_id=message.from_user.id, session=session)
    await state.set_data({"policies": policies})
    await message.answer(
        **content.as_kwargs(),
        reply_markup=create_policy_keyboard(True, *policies)
    )


@router.callback_query(PolicyAccess.filter())
async def policy_callback_handler(callback_query: CallbackQuery,
                                  callback_data: PolicyAccess,
                                  state: FSMContext, session: AsyncSession) -> None:
    logger.info(f"Received `Change Policy` callback from {callback_query.from_user.full_name} "
                f"ID: {callback_query.from_user.id}")
    user_id = callback_query.from_user.id
    policies = list((await state.get_data()).get("policies", await get_policies(user_id=user_id, session=session)))
    match callback_data.element:
        case "traffic":
            policies[0] = not policies[0]
        case "history":
            policies[1] = not policies[1]
        case "requests":
            policies[2] = not policies[2]
    await state.set_data({"policies": policies})
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup = create_policy_keyboard(True, *policies))


@router.callback_query(F.data == "confirm_policy")
async def confirm_policy_handler(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    logger.info(f"Received `Confirm Policy` callback from {callback_query.from_user.full_name} "
                f"ID: {callback_query.from_user.id}")
    user_id = callback_query.from_user.id
    user_policies = await get_policies(user_id=user_id, session=session)
    new_policies = (await state.get_data()).get("policies", user_policies)
    if user_policies == new_policies:
        await callback_query.message.answer("Your policies didn't change.")
    else:
        client = await session.get(Client, user_id)
        client.traffic_access, client.history_access, client.requests_access = new_policies
        await callback_query.message.answer("Your policies changed.")
        await session.commit()
    await callback_query.answer()