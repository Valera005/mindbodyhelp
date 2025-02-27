from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

feedback_callback = CallbackData("feedback", "order_id","to")

async def get_feedback_keyboard(order_id : int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Залишити відгук",callback_data=feedback_callback.new(order_id=order_id, to="give"))]
    ])
    return markup


feedback_finish_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Надіслати",callback_data=feedback_callback.new(order_id="", to="send"))],
        [InlineKeyboardButton(text="Назад", callback_data=feedback_callback.new(order_id="", to="back"))]
])

