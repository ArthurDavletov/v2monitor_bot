from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def client_manager_keyboard(any_users: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(callback_data = "add_client", text = "Add ➕")]
    if any_users:
        buttons.append(InlineKeyboardButton(callback_data = "remove_client", text = "Remove ❌"))
        # buttons.append(InlineKeyboardButton(callback_data = "edit_client", text = "Edit ✏"))  # not necessary
    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True)


def confirm_keyboard(action: Literal["add", "remove"]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(callback_data = f"confirm_{action}_clients", text = "Confirm ✅"),
        InlineKeyboardButton(callback_data = "cancel", text = "Cancel ❌")
    )
    return builder.as_markup(resize_keyboard = True)
