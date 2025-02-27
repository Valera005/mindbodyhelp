from aiogram.types import CallbackQuery

from keyboards.inline.verification_keyboard import verification_callback, get_confirmation_u_keyboard, \
    confirmation_verification_callback, get_verification_keyboard
from loader import dp, pool


@dp.callback_query_handler(verification_callback.filter())
async def confirm(call : CallbackQuery, callback_data : dict):
    await dp.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await get_confirmation_u_keyboard(prev_choice=callback_data["choice"], id = callback_data["id"]))

@dp.callback_query_handler(confirmation_verification_callback.filter(choice="0"))
async def confirm2(call: CallbackQuery, callback_data: dict):
    await dp.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await get_verification_keyboard(id = callback_data["id"]))

@dp.callback_query_handler(confirmation_verification_callback.filter(choice="1"))
async def confirm3(call: CallbackQuery, callback_data: dict):
    if callback_data["prev_choice"] == "1":
        async with pool.acquire() as conn:
            data = await conn.fetchrow(f'''update psychs set needs_verification = False, status = True where id = {callback_data["id"]} returning *''')
        await dp.bot.send_message(chat_id=data["user_id"], text="Ви успішно пройшли верифікацію, тепер вашу анкету будуть бачити клієнти\n\n"
                                                                "Долучайтесь до групи психологів, куди приходять сповіщення про запити з «Термінової допомоги»⬇️"
                                                                "https://t.me/+hBNqjZoJYZRkZmYy", disable_web_page_preview=True)
        try:
            await dp.bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,caption =  call.message.caption + "\n\n<b>✅ПРИЙНЯТО✅</b>", reply_markup=None)
        except TypeError:
            await dp.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + "\n\n<b>✅ПРИЙНЯТО✅</b>", reply_markup=None)

    elif callback_data["prev_choice"] =="0":
        async with pool.acquire() as conn:
            data = await conn.fetchrow(f'''Delete from psychs where id = {callback_data["id"]} returning *''')
        await dp.bot.send_message(chat_id=data["user_id"], text="Ви не пройшли верифікацію. Вашу анкету було видалено.")

        try:
            await dp.bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption =call.message.caption + "\n\n<b>❌ВІДМОВЛЕНО❌</b>", reply_markup=None)
        except TypeError:
            await dp.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + "\n\n<b>✅ПРИЙНЯТО✅</b>", reply_markup=None)
