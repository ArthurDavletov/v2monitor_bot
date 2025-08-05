from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_main_menu(is_admin: bool = False, history_access: bool = False,
                     traffic_access: bool = False, stats_access: bool = False) -> ReplyKeyboardMarkup:
    """Create the main menu keyboard."""
    builder = ReplyKeyboardBuilder()
    if is_admin:
        builder.row(KeyboardButton(text = "Status 🛠"), KeyboardButton(text = "All Stats 📊"))
    row_buttons = []
    if history_access:
        row_buttons.append(KeyboardButton(text = "History 📜"))
    if traffic_access:
        row_buttons.append(KeyboardButton(text = "Traffic 📈"))
    builder.row(*row_buttons)
    if stats_access:
        builder.row(KeyboardButton(text = "Requests's statistics 📈"))
    builder.row(KeyboardButton(text = "Settings ⚙️"), KeyboardButton(text = "Help ❓"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def settings_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Create the settings menu keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text = "Change Language 🌐"),
        KeyboardButton(text = "Change Policy 📜"),
    )
    if is_admin:
        builder.row(KeyboardButton(text = "Manage Clients 👥"))
    builder.row(KeyboardButton(text = "Back to Main Menu ↩️"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
