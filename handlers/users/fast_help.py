import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, Message, ReplyKeyboardRemove

from filters.call_filt import IsInUsers
from keyboards.default.request_contact_markup import request_contact_markup, request_contact_markup_2
from keyboards.inline.find_psych import get_requests2_keyboard, find_psych_callback
from keyboards.inline.for_channels import get_message_start_markup

from keyboards.inline.start_keyboard import start_callback, get_start_markup
from loader import dp, list_requests, fast_help_channel_id, pool
from states.psychs_state import RequestPhone2, FastHelp


@dp.callback_query_handler(start_callback.filter(ind="3"), ~IsInUsers())
async def req_number(call:CallbackQuery):
    await call.answer()
    await RequestPhone2.Q1.set()
    if call.from_user.username:
        await call.message.answer(text="Щоб продовжити шукати психолога, поділіться номером", reply_markup=request_contact_markup)
    else:
        await call.message.answer(
            text="Щоб продовжити шукати психолога, поділіться номером. \nАбо створіть собі юзернейм, в такому разі "
                 "ділитись номером буде необов'язково. Інструкція як це зробити - https://youtu.be/fc0HKwQASz8",
            reply_markup=request_contact_markup_2, disable_web_page_preview=True)

@dp.message_handler(text="Не ділитись номером телефону",state=RequestPhone2.Q1)
@dp.message_handler(content_types=ContentTypes.CONTACT,state=RequestPhone2.Q1)
async def req_cont(message : Message, state : FSMContext):
      async with pool.acquire() as conn:
        await conn.execute(f'''insert into users(user_id, username, phone_number) values({message.from_user.id}, '{message.from_user.username}', '{message.contact.phone_number if message.contact else "None"}')'''.replace("'None'","null"))
        await message.answer(text="Дякую", reply_markup=ReplyKeyboardRemove())
        await dp.bot.delete_message(chat_id=message.chat.id,message_id=message.message_id + 1)
        await state.reset_state(with_data=False)
        await state.update_data(requests_list=[])
        await message.answer(text='''
Оберіть Ваші запити⬇️

Запити: 
1. Панічні Атаки
2. Страх за себе, за рідних
3. Втома, неможливість сконцентруватися, відчай, бессилля, пригнічений стан, тривожність
4. Втрата сенсів, небажання жити
5. Як заспокоїтись?
6. Проблема вибору, правильного рішення (іхати, чи не іхати)
7. Що говорити дітям та підліткам (про війну, про смерть, як допомагати)?
8. Відчуття провини, сором, синдром того, що вижив. 
9. Як правильно підтримувати родичів на відстані
10. Фізичний біль''', reply_markup=await get_requests2_keyboard([]))


@dp.callback_query_handler(start_callback.filter(ind="3"))
async def first_q_2(call: CallbackQuery, state :FSMContext):
    async with pool.acquire() as conn:
        data = await conn.fetchrow(f'''select datetime < '{datetime.datetime.now() - datetime.timedelta(hours=1)}'::timestamp as is_allowed, datetime, user_id 
        from fast_help_orders where user_id = {call.from_user.id} order by id desc limit 1''')

    if data is not None and data["is_allowed"]==False and data["user_id"]!=698281804:
        await call.answer(text=f"Ви можете обрати психолога тільки 1 раз на годину. Наступного разу ви зможете шукати психолога через "
                               f"{int((datetime.timedelta(minutes=60) - (datetime.datetime.now() - data['datetime'])).total_seconds()/60)} хв", show_alert=True)
        return

    await call.answer()
    await state.update_data(requests_list=[])
    await FastHelp.S1.set()
    await call.message.edit_text(text=
'''Оберіть Ваші запити⬇️

Запити: 
1. Панічні Атаки
2. Страх за себе, за рідних
3. Втома, неможливість сконцентруватися, відчай, бессилля, пригнічений стан, тривожність
4. Втрата сенсів, небажання жити
5. Як заспокоїтись?
6. Проблема вибору, правильного рішення (іхати, чи не іхати)
7. Що говорити дітям та підліткам (про війну, про смерть, як допомагати)?
8. Відчуття провини, сором, синдром того, що вижив. 
9. Як правильно підтримувати родичів на відстані
10. Фізичний біль''', reply_markup=await get_requests2_keyboard([]))


@dp.callback_query_handler(find_psych_callback.filter(level = "1", con="1"), state = FastHelp.S1)
async def send_to_channel(call:CallbackQuery, state:FSMContext):
  async with pool.acquire() as conn:
    await call.message.edit_text("Ваш запит було надіслано в групу термінової допомоги, скоро з вами звяжуться", reply_markup=await get_start_markup(call.from_user.id))
    data = await state.get_data()

    sql = f'''insert into fast_help_orders(user_id, requests, datetime) values({call.from_user.id}, array{data["requests_list"]}::int[], 
    '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'::timestamp) returning id'''.replace("'None'", "null")

    async with pool.acquire() as con:
        fast_help_order_id =  await con.fetchval(sql)

    requests = "\n"
    for request_id in sorted(data["requests_list"], key=lambda x: int(x)):
        requests+= list_requests[request_id] + "\n"

    text = f'''
Потрібна термінова допомога
Інформація про людину:

Ім'я: {call.from_user.full_name}

Запити: {requests}
'''
    await dp.bot.send_message(text=text, chat_id=fast_help_channel_id, reply_markup=await get_message_start_markup(fast_help_order_id))
    await state.reset_state(with_data=True)






