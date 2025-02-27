from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, Message

from keyboards.inline.feedback_keyboards import feedback_callback, feedback_finish_keyboard
from keyboards.inline.start_keyboard import get_start_markup
from loader import dp, pool, feedback_channel_id
from states.psychs_state import Feedback


@dp.callback_query_handler(feedback_callback.filter(to="give"), state="*")
async def give_feedback_1(call : CallbackQuery, state : FSMContext, callback_data: dict):
    await call.answer()
    await state.reset_state()
    await state.update_data(order_id = callback_data["order_id"])
    await Feedback.Q1.set()
    await call.message.answer('''
Відповіді необхідно надати в одному повідомленні
    
1) Чи отримали Ви консультацію від психолога?
2) Ви задоволені консультацією?
3) напишіть що саме Вам сподобалось або Ви хотіли б покращити?
4) Плануєте продовжувати консультуватися у цього психолога?''')


@dp.message_handler(content_types=ContentTypes.TEXT, state=Feedback.Q1)
async def give_feedback_2(message : Message, state : FSMContext):
    await state.update_data(feedback=message.text)
    await message.answer("Вашу відповідь збережено, якщо хочете щось змінити натисніть 'Назад'.\n\nЩоб відправити натисніть 'Відправити'",reply_markup=feedback_finish_keyboard)

@dp.callback_query_handler(feedback_callback.filter(to="back"), state=Feedback.Q1)
async def give_feedback_1(call : CallbackQuery):
    await call.answer()
    await call.message.edit_text('''
Відповіді необхідно надати в одному повідомленні

1) Чи отримали Ви консультацію від психолога?
2) Ви задоволені консультацією?
3) напишіть що саме Вам сподобалось або Ви хотіли б покращити?
4) Плануєте продовжувати консультуватися у цього психолога?''')

@dp.callback_query_handler(feedback_callback.filter(to="send"), state=Feedback.Q1)
async def give_feedback_1(call : CallbackQuery, state : FSMContext):
    await call.answer("Дякуємо за відгук!")
    await call.message.edit_reply_markup()
    data = await state.get_data()
    await state.reset_state()

    await call.message.edit_text(text="Хто Ви?", reply_markup=await get_start_markup(call.from_user.id))

    async with pool.acquire() as conn:
        await conn.execute(f'''update orders set feedback = '{data["feedback"].replace("'","''")}' where id = {data["order_id"]}''')
        data_2 = await conn.fetchrow(f'''select orders.id, orders.feedback, psychs.pib, psychs.user_id psych_user_id, psychs.username psych_username, 
        psychs.phone_number psych_phone_number, users.user_id, users.username, users.phone_number, 
        users.full_name from orders inner join psychs on orders.psych_user_id = psychs.user_id 
        inner join users on orders.user_id = users.user_id where orders.id = {data["order_id"]}''')

    await dp.bot.send_message(chat_id=feedback_channel_id, text=f'''
Айді замовлення: {data_2["id"]}

Клієнт 
Імʼя: <a href='tg://user?id={data_2["user_id"]}'>{data_2["full_name"] if data_2["full_name"] else "Невідомо"}</a>
{("Юзернейм: @" + data_2["username"]) if data_2["username"] else ""}
{("Номер телефону: " + data_2["phone_number"]) if data_2["phone_number"] else ""}

Психолог
Імʼя: <a href='tg://user?id={data_2["psych_user_id"]}'>{data_2["pib"] if data_2["pib"] else "Невідомо"}</a>
{("Юзернейм: @" + data_2["psych_username"]) if data_2["psych_username"] else ""}
{("Номер телефону: " + data_2["psych_phone_number"]) if data_2["psych_phone_number"] else ""}

Відгук:

{data_2["feedback"]}
''')




