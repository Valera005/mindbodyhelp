from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import pool

start_callback = CallbackData("start","ind")

to_menu_callback = CallbackData("to_menu")


async def get_start_markup(user_id):
  async with pool.acquire() as conn:
    is_exist = await conn.fetchval(f'''SELECT exists (SELECT 1 FROM psychs WHERE user_id = {user_id} LIMIT 1)''')
  if is_exist:
      start_markup = InlineKeyboardMarkup(inline_keyboard=[
          [InlineKeyboardButton(text="Моя анкета", callback_data=start_callback.new(ind="0"))],
          [InlineKeyboardButton(text="Я шукаю психолога", callback_data=start_callback.new(ind=2))],
          [InlineKeyboardButton(text="🔔 Термінова допомога", callback_data=start_callback.new(ind=3))]
      ])
  else:
      start_markup = InlineKeyboardMarkup(inline_keyboard=[
          [InlineKeyboardButton(text="Я психолог", callback_data=start_callback.new(ind="psych_reg"))],
          [InlineKeyboardButton(text="Я шукаю психолога", callback_data=start_callback.new(ind=2))],
          [InlineKeyboardButton(text="🔔 Термінова допомога", callback_data=start_callback.new(ind=3))]
      ])
  return start_markup







