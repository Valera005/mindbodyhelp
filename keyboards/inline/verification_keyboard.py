from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

confirmation_verification_callback = CallbackData("conf_u", "choice", "prev_choice", "id")
verification_callback = CallbackData("verif", "id", "choice")

async def get_verification_keyboard(id : int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Прийняти", callback_data=verification_callback.new(id=id, choice="1"))],
        [InlineKeyboardButton(text="Відмовити", callback_data=verification_callback.new(id=id, choice="0"))]
    ])
    return markup

async def get_confirmation_u_keyboard(prev_choice, id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Так", callback_data=confirmation_verification_callback.new(choice="1", prev_choice = prev_choice, id = id))],
        [InlineKeyboardButton(text="Назад", callback_data=confirmation_verification_callback.new(choice="0", prev_choice = prev_choice, id = id))]
    ])
    return markup