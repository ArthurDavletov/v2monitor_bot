from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_main_menu() -> ReplyKeyboardMarkup:
    """Create the main menu keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton("Stats"), KeyboardButton("Status"))
    builder.row(KeyboardButton("Settings"), KeyboardButton("Help"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def settings_menu() -> ReplyKeyboardMarkup:
    """Create the settings menu keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton("Change Language"), KeyboardButton("Back to Main Menu"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

