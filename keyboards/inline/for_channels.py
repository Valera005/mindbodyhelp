from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

channel_confirmation_callback = CallbackData("chan", "choice", "fast_help_order_id")


async def get_message_start_markup(fast_help_order_id):
    message_start_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Взяти запит", callback_data=channel_confirmation_callback.new(choice = "finish", fast_help_order_id=fast_help_order_id))]
    ])
    return message_start_markup


async def get_message_confirmation_markup(fast_help_order_id):
    message_confirmation_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Так",callback_data=channel_confirmation_callback.new(choice = "1", fast_help_order_id=fast_help_order_id))],
    [InlineKeyboardButton(text="Ні", callback_data=channel_confirmation_callback.new(choice = "0", fast_help_order_id=fast_help_order_id))]
    ])
    return message_confirmation_markup