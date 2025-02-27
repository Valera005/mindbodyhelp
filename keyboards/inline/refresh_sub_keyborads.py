from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

refresh_sub_callback = CallbackData("refresh")

def get_refresh_sub_callback():
    return refresh_sub_callback.new()


refresh_sub_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Поновити підписку", callback_data=get_refresh_sub_callback())]
])
