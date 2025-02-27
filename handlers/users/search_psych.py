import asyncio
import logging
import datetime

from datetime import date


from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, MessageToDeleteNotFound, MessageCantBeDeleted


from filters.call_filt import IsInUsers, IsFirstPsych
from keyboards.default.request_contact_markup import request_contact_markup, request_contact_markup_2

from keyboards.inline.find_psych import get_requests2_keyboard, find_psych_callback, get_ages_key_2, get_language_key_2, \
    get_work_condition_key_2, get_psych_find_key_2
from keyboards.inline.psych_poll_keyboards import pre_poll_keyboard, pre_poll_callback
from keyboards.inline.start_keyboard import start_callback, get_start_markup
from loader import dp, list_requests, pool, exceptions_chat_id, scheduler
from states.psychs_state import RequestPhone, PrePollUser
from utils.dop_functions import send_feedback_message


@dp.callback_query_handler(start_callback.filter(ind="2"), ~IsInUsers(), state='*')
async def show_info(call:CallbackQuery):
    await PrePollUser.Q1.set()
    await call.message.edit_text('''
Добрий день.

Ви зайшли у меню для Пошуку психолога. 

Заповнюючи анкету (натискаючи кнопку "Далі") Ви погоджуєтесь на правила користування. Даєте згоду на обробку ваших даних. 
Весь опис правил Ви знайдете за командою /info''',reply_markup=pre_poll_keyboard)

@dp.message_handler(text="Назад", state = RequestPhone.Q1)
async def show_info_2(message : Message):
    await PrePollUser.Q1.set()
    await message.answer('''
Добрий день.

Ви зайшли у меню для Пошуку психолога. 

Заповнюючи анкету Ви погоджуєтесь на правила користування. Даєте згоду на обробку ваших даних. 
Весь опис правил Ви знайдете за командою /info''',reply_markup=pre_poll_keyboard)

@dp.callback_query_handler(pre_poll_callback.filter(to="poll"), state=PrePollUser.Q1)
async def req_number(call:CallbackQuery):
    await call.answer()
    await RequestPhone.Q1.set()
    if call.from_user.username:
        await call.message.answer(text="Щоб продовжити шукати психолога, поділіться номером",reply_markup=request_contact_markup)
    else:
        await call.message.answer(text="Щоб продовжити шукати психолога, поділіться номером. \nАбо створіть собі юзернейм, в такому разі "
                                       "ділитись номером буде необов'язково. Інструкція як це зробити - https://youtu.be/fc0HKwQASz8",
                                  reply_markup=request_contact_markup_2, disable_web_page_preview=True)

@dp.message_handler(text="Не ділитись номером телефону",state=RequestPhone.Q1)
@dp.message_handler(content_types=ContentTypes.CONTACT,state=RequestPhone.Q1)
async def req_cont(message : Message, state : FSMContext):
      async with pool.acquire() as conn:
        await conn.execute(f'''insert into users(user_id, username, phone_number, full_name, date_of_registration) values({message.from_user.id}, '{message.from_user.username}', 
        '{message.contact.phone_number if message.contact else "None"}', '{message.from_user.full_name.replace("'","''")}', '{date.today()}'::date)'''.replace("'None'","null"))
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


@dp.callback_query_handler(start_callback.filter(ind="2"))
async def first_q_2(call: CallbackQuery, state: FSMContext):
    async with pool.acquire() as conn:
        data = await conn.fetchrow(f'''select datetime < '{datetime.datetime.now() - datetime.timedelta(hours=1)}'::timestamp as is_allowed, datetime, user_id from orders where user_id = {call.from_user.id} order by id desc limit 1''')

    if data is not None and data["is_allowed"]==False and data["user_id"]!=698281804:
        await call.answer(text=f"Ви можете обрати психолога тільки 1 раз на годину. Наступного разу ви зможете шукати психолога через "
                               f"{int((datetime.timedelta(minutes=60) - (datetime.datetime.now() - data['datetime'])).total_seconds()/60)} хв", show_alert=True)
        return

    await call.answer()
    async with state.proxy() as data:
        if "requests_list" not in data.keys():
            data["requests_list"] = []

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
10. Фізичний біль''', reply_markup=await get_requests2_keyboard(data["requests_list"]))

@dp.callback_query_handler(find_psych_callback.filter(level="1", con = ''), state="*")
async def react_req(call:CallbackQuery, callback_data : dict, state : FSMContext):
    await call.answer()
    markup = call.message.reply_markup
    async with state.proxy() as data:
        ind = int(callback_data["req_id"]) - 1
        if callback_data["req_id"] not in data["requests_list"]:
            markup.inline_keyboard[ind][0].text = markup.inline_keyboard[ind][0].text.replace("❌","✅")
            data["requests_list"].append(callback_data["req_id"])
        else:
            markup.inline_keyboard[ind][0].text = markup.inline_keyboard[ind][0].text.replace("✅", "❌")
            data["requests_list"].remove(callback_data["req_id"])
    try:
        await call.message.edit_reply_markup(markup)
    except MessageNotModified:
        pass


@dp.callback_query_handler(find_psych_callback.filter(level="1", con="1"))
async def second_q_2(call:CallbackQuery, state : FSMContext):
    data = await state.get_data()
    if not data["requests_list"]:
        await call.answer("Виберіть хоча б один запит")
        return
    await call.answer()
    try:
        await call.message.edit_text(text="Вкажіть Ваш вік ⬇️", reply_markup=await get_ages_key_2())
    except MessageNotModified as exc:
        logging.exception(exc)
        dp.bot.send_message(chat_id=exceptions_chat_id, text=exc)

@dp.callback_query_handler(find_psych_callback.filter(level="2"))
async def third_q_2(call:CallbackQuery,callback_data:dict):
    await call.answer(cache_time=1)
    await call.message.edit_text("Яка Ваша мова спілкування? ⬇️", reply_markup=await get_language_key_2(callback_data))


@dp.callback_query_handler(find_psych_callback.filter(level='5', choice = '3'), IsFirstPsych())
@dp.callback_query_handler(find_psych_callback.filter(level='3'))
async def fourth_q_2(call:CallbackQuery,callback_data:dict):
    await call.answer(cache_time=1)

    try:
        await call.message.delete()
    except MessageToDeleteNotFound as e:
        logging.exception(e)
        return
    except MessageCantBeDeleted as e:
        logging.exception(e)

    await call.message.answer("Вкажіть які умови Вам підходять? ⬇️", reply_markup=await get_work_condition_key_2(callback_data))


@dp.callback_query_handler(find_psych_callback.filter(level='5', choice = '3'))
async def back_results(call:CallbackQuery, callback_data : dict, state : FSMContext):
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        data["ind"] -=1
        data["psych_id"] = data["swiped_id"][data["ind"]]

    sql = f'''select *, competence & array{data["requests_list"]}::int[] as inter from psychs where user_id = {data['swiped_id'][data['ind']]}'''
    async with pool.acquire() as conn:
        cv = await conn.fetchrow(sql)

    competences = "\n"
    for competence, x in enumerate(cv["inter"], 1):
        s = list_requests[str(competence)]
        competences += str(x)+". "+s[s.find('.')+2:]+"\n"

    text = f'''
ПІБ: {cv["pib"]}

Ціна констультації: {str(cv["price"]) + " грн" if cv["price"] else "договірна" if data["pay"]=="2" else "без оплати"}

Ваші запити, з якими цей психолог працює: {competences}
Про себе: 

{cv["description"]}'''

    try:
        await call.message.delete()
    except MessageToDeleteNotFound as e:
        logging.exception(e)
        return
    except MessageCantBeDeleted as e:
        pass
    if cv["photo_file_id"]:
        await call.message.answer_photo(photo=cv["photo_file_id"], caption=text, reply_markup=await get_psych_find_key_2(callback_data))
    else:
        await call.message.answer(text=text, reply_markup=await get_psych_find_key_2(callback_data), disable_web_page_preview=True)


@dp.callback_query_handler(find_psych_callback.filter(level='5', choice="1"))
@dp.callback_query_handler(find_psych_callback.filter(level='4'))
async def show_results(call:CallbackQuery, callback_data : dict, state : FSMContext):
  await call.answer(cache_time=1)
  async with state.proxy() as data:
    if callback_data["level"]=="4":
        data.update(callback_data,swiped_id = [], ind = -1)

    is_add = False
    if data['ind']==len(data['swiped_id'])-1:
        is_add = True
        sql = f'''select *, competence & array{data["requests_list"]}::int[] as inter from psychs where competence && array{data["requests_list"]}::int[] and ages @> array[{data["age_id"]}] 
            {"and pay_variant=1" if data["pay"] == "1" else ""} {f"and (language={data['language']} or language=3)" if data['language'] != '3' else ""} and status = true
            and (not array[user_id] <@ array{data["swiped_id"]}::bigint[]) and needs_verification = false and date_of_expiration is not null and current_date - date_of_expiration <=0
            order by array_length((select competence & array{data["requests_list"]}::int[]),1) DESC, random() limit 1'''
    else:
        data["ind"] += 1
        sql = f'''select *, competence & array{data["requests_list"]}::int[] as inter from psychs where user_id = {data['swiped_id'][data['ind']]}'''

    async with pool.acquire() as conn:
        cv = await conn.fetchrow(sql)

    if cv is None:
        await call.message.answer(text="Вибачте, більше не залишилось психологів, які задовільняють ваші запити.")
        return



    if is_add:
        data["swiped_id"].append(cv["user_id"])
        data["ind"] += 1



    competences = "\n"
    for competence, x in enumerate(cv["inter"], 1):
        s = list_requests[str(competence)]
        competences += str(x)+". "+s[s.find('.')+2:]+"\n"

    text = f'''
ПІБ: {cv["pib"]}

Ціна констультації: {str(cv["price"]) + " грн" if cv["price"] else "договірна"}

Ваші запити, з якими цей психолог працює: {competences}
Про себе: 

{cv["description"]}'''

    if callback_data["level"]=="4":
        await call.message.edit_text(text=
'''Щоб зв'язатись з психологом:
• перейдіть за посиланням (клік на його ПІБ) 
AБО
• додайте телефон в свої контакти в телеграм, інструкція як це зробити - https://youtu.be/f7f_uc8wZE0
АБО
• зателефонуйте на вказаний номер
                          
Контактні дані психолога ви побачите коли натисните на кнопку "Дякую, цей психолог мені підходить"  
                        
P.S. В боті реалізована система релевантного пошуку, тобто спочатку ви побачите психологів, які відповідають на найбільшу кількість ваших запитів''',disable_web_page_preview=True)
        await asyncio.sleep(2)
        if cv["photo_file_id"]:
            await call.message.answer_photo(photo= cv["photo_file_id"], caption = text[0:1022], reply_markup=await get_psych_find_key_2(callback_data))
        else:
            await call.message.answer(text=text, reply_markup=await get_psych_find_key_2(callback_data), disable_web_page_preview=True)
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            return
        except MessageCantBeDeleted:
            pass
        if cv["photo_file_id"]:
            await call.message.answer_photo(photo= cv["photo_file_id"], caption = text[0:1022], reply_markup=await get_psych_find_key_2(callback_data))
        else:
            await call.message.answer(text=text, reply_markup=await get_psych_find_key_2(callback_data), disable_web_page_preview=True)



@dp.callback_query_handler(find_psych_callback.filter(level = "5", choice="2"))
async def i_find(call:CallbackQuery, state:FSMContext, callback_data : dict):
    await call.answer()
    try:
        await call.message.delete()
    except MessageToDeleteNotFound as e:
        logging.exception(e)
        return
    except MessageCantBeDeleted as e:
        logging.exception(e)
    data = await state.get_data()
    async with pool.acquire() as conn:

        cv = await conn.fetchrow(f'''select *, competence & array{data["requests_list"]}::int[] as inter from psychs where user_id = {data["swiped_id"][data["ind"]]}''')

        sql = f'''insert into orders(user_id, psych_user_id, requests, age, language, pay_variant,datetime,price) values(
        {call.from_user.id}, {data["swiped_id"][data["ind"]]}, array{data["requests_list"]}::int[], {data["age_id"]},{data["language"]}, 
        {int(data["pay"])},'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, {cv["price"] if cv["price"] else "'None'"}) returning id'''.replace("'None'","null")

        order_id = await conn.fetchval(sql)

        phone_number = await conn.fetchval(f'''select phone_number from users where user_id = {call.from_user.id}''')
        competences = "\n"
        for competence, x in enumerate(cv["inter"], 1):
            s = list_requests[str(competence)]
            competences += str(x) + ". " + s[s.find('.') + 2:] + "\n"

        #{("Номер телефону: " + phone_number) if phone_number else ""}
        try:
            await dp.bot.send_message(chat_id=data["swiped_id"][data["ind"]], text=f'''
На вашу анкети відгукнувся клієнт {call.from_user.get_mention(as_html=True)}
{("Юзернейм: @"+call.from_user.username) if call.from_user.username else ""}
{"Умови: Платна консультація" if data["pay"]=="2" else "Умови: Перша зустріч без оплати (45 хв)"}

з запитами: {competences}

Клієнт зконтактує з Вами. 

Якщо Ви не можете взяти цього клієнта з технічних або особистих причин, будь ласка напишіть адміністратору  @marina_mindbody.
Дякуємо
''')
        except BotBlocked:
            await call.message.answer(text="Данний психолог заблокував бота, тому ми не впевнені чи надає він зараз послуги")
            await conn.execute(f'''update psychs set status = false where user_id = {data["swiped_id"][data["ind"]]}''')



    text = f'''
Надсилаємо контактні дані Вашого психолога.

ПІБ: <a href='tg://user?id={cv["user_id"]}'>{cv["pib"]}</a>
{f"Юзернейм: @{cv['username']}" if cv['username'] is not None else ""}
{f"Номер телефону: {cv['phone_number']}" if cv["phone_number"] else ""}

Ціна констультації: {str(cv["price"]) + " грн" if cv["price"] else "договірна" if data["pay"]=="2" else "без оплати"}

Ваші запити, з якими цей психолог працює: {competences}
Про себе: 

{cv["description"]}'''

    if cv["photo_file_id"]:
        await call.message.answer_photo(photo=cv["photo_file_id"], caption=text[0:1022])
    else:
        await call.message.answer(text=text, disable_web_page_preview=True)
    await call.message.answer('''
<b>ВАЖЛИВО</b> 

Зв'яжіться з психологом для продовження спілкування! 

Ми не надсилаємо Ваші контакти психологу задля безпеки персональних даних.

Якщо у Вас виникли технічні чи організаційні питання, будь ласка напишіть адміністратору @marina_mindbody''')
    await call.message.answer(text="Хто Ви?", reply_markup=await get_start_markup(call.from_user.id))
    await state.reset_state(with_data=True)



    scheduler.add_job(send_feedback_message, trigger="date", run_date=datetime.datetime.now()+datetime.timedelta(days=3),
                      kwargs={"order_id":order_id, "chat_id" : call.message.chat.id, "pib":cv["pib"], "user_id" : cv["user_id"]})



