import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, Message
from asyncio import sleep

from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

from keyboards.inline.my_cv_keyboards import get_my_cv_key, my_cv_callback, edit_cv_callback, get_things_keyboard, \
    get_edit_requests_key, get_edit_ages_key, edit_cv_go_back_keyboard, delete_my_cv_confirmation_keyboard, \
    universal_confirmation_callback
from keyboards.inline.start_keyboard import start_callback, get_start_markup
from loader import dp, list_requests, list_ages, list_languages, pool
from states.psychs_state import EditCv


@dp.callback_query_handler(my_cv_callback.filter(id="1"))
@dp.callback_query_handler(start_callback.filter(ind="0"))
async def my_cv_show(call : CallbackQuery, callback_data : dict, state : FSMContext):
    await call.answer(cache_time=1)
    async with pool.acquire() as conn:
        if callback_data["@"] == "my_cv" and callback_data["id"] == "1":
            data = await conn.fetchrow(f'''UPDATE psychs SET status = NOT status WHERE user_id ={call.from_user.id} returning *''')
        else:
            data = await conn.fetchrow(f'''select * from psychs where user_id = {call.from_user.id}''')

    competences = "\n"
    for competence in data["competence"]:
        competences += list_requests[str(competence)] + "\n"

    ages = ""
    for age in data["ages"]:
        ages+=list_ages[str(age)]+", "

#Умови роботи: {"Тільки з оплатою" if data["pay_variant"]==2 else "Можна й без оплати"}
    text = f'''
ПІБ: {data["pib"]}\n
Ціна констультації: {str(data["price"]) + " грн" if data["price"] else "без оплати"}

Запити: {competences}
Вік людей: {ages[:-2]}

Мова: {list_languages[str(data["language"])]}
{f"Номер телефону: {data['phone_number']}" if data["phone_number"] else ""}
Про себе:
{data['description']}

Статус: {"На верифікації" if data["needs_verification"] else "Включена" if data["status"] else "Выключена" } 
(від цього залежить чи будуть люди бачити анкету)
'''

    await state.set_data({"pay_variant" : data["pay_variant"]})
    try:
        await call.message.delete()
    except MessageToDeleteNotFound as e:
        logging.exception(e)
        return
    except MessageCantBeDeleted as e:
        logging.exception(e)
    if data["photo_file_id"]:
        await call.message.answer_photo(photo=data["photo_file_id"], caption=text[0:1022], reply_markup=await get_my_cv_key(data["status"]))
    else:
        await call.message.answer(text= text, reply_markup=await get_my_cv_key(data["status"]), disable_web_page_preview=True)
    await state.reset_state()



@dp.callback_query_handler(edit_cv_callback.filter(to="back"), state=EditCv.all_states + tuple([None]))
@dp.callback_query_handler(my_cv_callback.filter(id = "2"), state=EditCv.all_states + tuple([None]))
async def edit_cv(call : CallbackQuery, state : FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        logging.exception("_________________________MessageToDeleteNotFound_________________________")
    await call.message.answer("Оберіть що ви хочете оновити",reply_markup=get_things_keyboard())
    await state.reset_state(with_data=False)

async def finish_edit_cv_message(message : Message, state : FSMContext):
    await message.answer("Оберіть що ви хочете оновити", reply_markup=get_things_keyboard())
    await state.reset_state(with_data=False)

@dp.callback_query_handler(edit_cv_callback.filter(thing="req"))
async def edit_req_list(call:CallbackQuery, state : FSMContext):
    await EditCv.EditReqList.set()
    async with state.proxy() as data:
        data.update(requests_list=[])

        await call.message.edit_text(text=
'''Вкажіть Вашу спеціалізацію /запити, з якими готові працювати⬇️
                              
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
10. Фізичний біль''', reply_markup=await get_edit_requests_key(data["requests_list"]))

@dp.callback_query_handler(edit_cv_callback.filter(to="finish_req"), state=EditCv.EditReqList)
async def edit_req_list_2(call:CallbackQuery, state : FSMContext):
    data = await state.get_data()
    async with pool.acquire() as conn:
        await conn.execute(f'''update psychs set competence = ARRAY{sorted(data["requests_list"], key=int)}::int[] where user_id = {call.from_user.id}''')
    await call.answer(text="Запити, з якими ви працюєте, було успішно оновлено")
    await edit_cv(call, state)

@dp.callback_query_handler(edit_cv_callback.filter(thing="age"))
async def edit_age_list(call:CallbackQuery, state : FSMContext):
    await EditCv.EditAgeList.set()
    async with state.proxy() as data:
        data.update(ages_list=[])
        await call.message.edit_text(text='''Допустимий вік клієнтів⬇️''', reply_markup=await get_edit_ages_key(data["ages_list"]))

@dp.callback_query_handler(edit_cv_callback.filter(to="finish_age"), state=EditCv.EditAgeList)
async def edit_req_list_2(call:CallbackQuery, state : FSMContext):
    data = await state.get_data()
    async with pool.acquire() as conn:
        await conn.execute(f'''update psychs set ages = ARRAY{sorted(data["ages_list"], key=int)}::int[] where user_id = {call.from_user.id}''')
    await call.answer(text="Вік людей, з якими ви працюєте, було успішно оновлено")
    await edit_cv(call, state)

@dp.callback_query_handler(edit_cv_callback.filter(thing="username"))
async def edit_username(call:CallbackQuery):
    if call.from_user.username:
        async with pool.acquire() as conn:
           await conn.execute(f'''update psychs set username = '{call.from_user.username}' where user_id = {call.from_user.id}''')
        await call.answer(text="Ваш юзернейм було оновлено на поточний", cache_time=3)
    else:
        await call.answer(text="Помилка, у вас немає юзернейму")

@dp.callback_query_handler(edit_cv_callback.filter(thing="photo"))
async def edit_photo(call:CallbackQuery):
    await EditCv.EditPhoto.set()
    await call.message.edit_text(text='''Надішліть нове фото''', reply_markup=edit_cv_go_back_keyboard)

@dp.message_handler(content_types=ContentTypes.PHOTO, state=EditCv.EditPhoto)
async def edit_photo_2(message: Message, state :FSMContext):
    async with pool.acquire() as conn:
        await conn.execute(f'''update psychs set photo_file_id = '{message.photo[-1].file_id}' where user_id = {message.from_user.id}''')

    await message.answer("Фото було успішно оновлено")
    await sleep(1)
    await finish_edit_cv_message(message, state)

@dp.callback_query_handler(edit_cv_callback.filter(thing="phone_number"))
async def edit_phone_number(call:CallbackQuery):
    await EditCv.EditPhoneNumber.set()
    await call.message.edit_text("Напишіть новий номер телефону в міжнарожному форматі\nНаприклад: +380123456789", reply_markup=edit_cv_go_back_keyboard)

@dp.message_handler(content_types=ContentTypes.TEXT, state=EditCv.EditPhoneNumber)
async def edit_phone_number_2(message:Message, state : FSMContext):
    if not message.entities or message.entities[0].type!="phone_number":
        await message.answer("Помилка, в вашому повідомленні не виялено номеру телефону")
        return
    if message.entities[0].length<11:
        await message.answer("Помилка, номер телефону необхідно написати в міжнародному форматі")
        return

    async with pool.acquire() as conn:
        await conn.execute(f'''update psychs set phone_number = '{message.entities[0].get_text(message.text)}' where user_id = {message.from_user.id}''')
    await message.answer("Ваш номер телефону було успішно оновлено")
    await finish_edit_cv_message(message, state)

@dp.callback_query_handler(edit_cv_callback.filter(thing="price"))
async def edit_price(call:CallbackQuery):
    await call.message.answer("Введіть ціну консультації у грн\nНаприклад: 400")
    await EditCv.EditPrice.set()

@dp.message_handler(content_types=ContentTypes.TEXT, state=EditCv.EditPrice)
async def edit_price_2(message: Message, state :FSMContext):
    async with pool.acquire() as conn:
        try:
            await conn.execute(f'''update psychs set price = '{int(message.text)}' where user_id = {message.from_user.id}''')
        except ValueError:
            await message.answer("Ціну не було виявлено, введіть лише число")
            return

    await message.answer("Ціну за консультацію було успішно оновлено")
    await sleep(1)
    await finish_edit_cv_message(message, state)


@dp.callback_query_handler(edit_cv_callback.filter(thing="description"))
async def edit_description(call:CallbackQuery):
    await EditCv.EditDescription.set()
    await call.message.edit_text(text='''Надішліть опис про себе''', reply_markup=edit_cv_go_back_keyboard)

@dp.message_handler(content_types=ContentTypes.TEXT, state=EditCv.EditDescription)
async def edit_description_2(message: Message, state :FSMContext):
    async with pool.acquire() as conn:
        await conn.execute(f'''update psychs set description = '{message.text}' where user_id = {message.from_user.id}''')

    await message.answer("Опис було успішно оновлено")
    await sleep(1)
    await finish_edit_cv_message(message, state)

@dp.callback_query_handler(edit_cv_callback.filter(thing="delete_cv"))
async def edit_age_list(call:CallbackQuery, state : FSMContext):
    await call.message.edit_text(text='''
Ви впевнені, що бажаєте видалити свою анкету ? 
Цю дію не можливо буде відмінити. 
Якщо у вас є оплачений період, Ви його втратите.''', reply_markup= delete_my_cv_confirmation_keyboard)


@dp.callback_query_handler(universal_confirmation_callback.filter(where = "delete_my_cv", choice = "1"))
async def delete_cv(call:CallbackQuery,state : FSMContext):
    sql = f'''insert into deleted_psychs(user_id, username, pib, competence, ages, language, pay_variant, phone_number, description, 
						   photo_file_id, date_of_expiration, date_of_registration) 
						   select user_id, username, pib, competence, ages, language, pay_variant, phone_number, description, 
						   photo_file_id, date_of_expiration, date_of_registration from psychs where user_id = {call.from_user.id}'''
    sql2 = f'''delete from psychs where user_id = {call.from_user.id}'''

    async with pool.acquire() as conn:
        await conn.execute(sql)
        await conn.execute(sql2)

    await call.answer("Ваша анкета була успішно видалена", show_alert=True, cache_time=3)
    await call.message.answer(text="Хто Ви?", reply_markup=await get_start_markup(call.from_user.id))
