from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_policy_keyboard() -> InlineKeyboardMarkup:
    """Create the policy keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton("Privacy Policy", callback_data="privacy_policy"))
    builder.add(InlineKeyboardButton("Terms of Service", callback_data="terms_of_service"))
    return builder.as_markup()
