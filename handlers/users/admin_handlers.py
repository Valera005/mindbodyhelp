from aiogram.types import Message

from keyboards.inline.refresh_sub_keyborads import refresh_sub_keyboard
from loader import dp


@dp.message_handler(commands=['admin'], chat_id = [698281804])
async def admin_h_1(message: Message):
    await dp.bot.send_message(chat_id=698281804,
                        text='Термін дії вашої підписки закінчився. Щоб продовжити підписку натисніть на кнопку знизу\n\n',
                        reply_markup=refresh_sub_keyboard)