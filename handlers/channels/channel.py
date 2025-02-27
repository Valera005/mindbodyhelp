from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import BotBlocked

from keyboards.inline.for_channels import channel_confirmation_callback, get_message_confirmation_markup, \
    get_message_start_markup
from loader import dp, pool


@dp.callback_query_handler(channel_confirmation_callback.filter(choice="finish"))
async def change_markup(call:CallbackQuery, callback_data : dict):
    await call.message.edit_reply_markup(reply_markup=await get_message_confirmation_markup(callback_data["fast_help_order_id"]))

@dp.callback_query_handler(channel_confirmation_callback.filter(choice="1"))
async def change_status(call:CallbackQuery, callback_data : dict):
    async with pool.acquire() as con:
        data = await con.fetchrow(f'''update fast_help_orders set psych_user_id = {call.from_user.id} where id = {callback_data["fast_help_order_id"]} returning *''')
        data_user = await con.fetchrow(f'''select phone_number, username from users where user_id = {data['user_id']}''')

    try:
        await dp.bot.send_message(chat_id=call.from_user.id, text= "Ось контакти людини, яка запросила термінову допомогу:\n"
                                                                   f"ПІБ: <a href='tg://user?id={data['''user_id''']}'>{call.from_user.full_name}</a>\n"
                                                                   f"Юзернейм: @{data_user['username']}\n"
                                                                   f"Номер телефону: {data_user['phone_number'] if data_user['phone_number'] else 'Немає'}")
    except BotBlocked:
        await dp.bot.send_message(chat_id=528984687, text="Видаліть данного психолога з групи швидкої допомоги\n"
                                                          f"{call.from_user.get_mention(as_html=True)}\n"
                                                          f"@{call.from_user.username}")

    await call.message.edit_text(text=call.message.html_text+f'''\n\n✅✅✅✅✅✅\nОПРАЦЬОВАНО: {call.from_user.get_mention(as_html=True)}
{f"Юзернейм психолога: @{call.from_user.username}" if call.from_user.username else ""}''',reply_markup=None)


@dp.callback_query_handler(channel_confirmation_callback.filter(choice="0"))
async def change_to_1(call:CallbackQuery, callback_data : dict):
    await call.message.edit_reply_markup(reply_markup=await get_message_start_markup(callback_data["fast_help_order_id"]))