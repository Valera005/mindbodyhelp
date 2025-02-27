import datetime

from aiogram.types import CallbackQuery, LabeledPrice, ContentTypes, Message

from data.config import PROVIDER_TOKEN
from filters import Payload
from keyboards.inline.refresh_sub_keyborads import refresh_sub_callback
from keyboards.inline.start_keyboard import get_start_markup
from loader import dp, admins, pool


@dp.callback_query_handler(refresh_sub_callback.filter())
async def refresh_sub_1(call:CallbackQuery):
    await call.answer()
    amount = 300_00

    if call.from_user.id in admins:
        amount = int(amount / 100)

    await dp.bot.send_invoice(chat_id=call.message.chat.id, title='Продовження підписки', description='Термін продовження: 1 місяць', payload="3",
                              provider_token=PROVIDER_TOKEN, currency='UAH',prices=[LabeledPrice(label='Оплата за продовження підписки', amount=amount)], protect_content=True)

@dp.message_handler(Payload("3"), content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def refresh_sub_1(message : Message):

    async with pool.acquire() as con:
        is_date_of_exp_in_future = await con.fetchval(f"select (date_of_expiration>current_date) from psychs where user_id = {message.from_user.id}")
        if is_date_of_exp_in_future:
            new_date : datetime.datetime = await con.fetchval(f"update psychs set date_of_expiration = date_of_expiration+30, is_reminded = false where user_id = {message.from_user.id} returning date_of_expiration")
        else:
            new_date : datetime.datetime = await con.fetchval(f"update psychs set date_of_expiration = current_date+30, is_reminded = false where user_id = {message.from_user.id} returning date_of_expiration")
    await message.answer(text = f'Вашу підписку продовжено до: {new_date.strftime("%d.%m.%Y")}')
    await message.answer(text="Хто Ви?", reply_markup=await get_start_markup(message.from_user.id))
