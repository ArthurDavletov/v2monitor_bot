from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


class PolicyAccess(CallbackData, prefix="access"):
    element: str


def create_policy_keyboard(is_logs_available: bool = True,
                           traffic_access: bool = False,
                           history_access: bool = False,
                           requests_access: bool = False) -> InlineKeyboardMarkup:
    """Create the policy keyboard."""
    s = ("❌", "✅")
    builder = InlineKeyboardBuilder()
    builder.button(
        text = f"{s[traffic_access]} Access to traffic usage",
        callback_data = PolicyAccess(element = "traffic")
    )
    if is_logs_available:
        builder.button(
            text = f"{s[history_access]} Access to the history",
            callback_data = PolicyAccess(element = "history")
        )
        builder.button(
            text = f"{s[requests_access]} Access to the count of requests",
            callback_data = PolicyAccess(element = "requests")
        )
    builder.button(text = "▶ Confirm", callback_data = "confirm_policy")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()
