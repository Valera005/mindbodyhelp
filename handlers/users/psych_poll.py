import logging
from datetime import date, timedelta


from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ContentTypes, MediaGroup, LabeledPrice, \
    PreCheckoutQuery
from aiogram.utils.exceptions import MessageNotModified

from data.config import PROVIDER_TOKEN
from filters import Payload

from keyboards.default.request_contact_markup import request_contact_markup, back_keyboard, forward_back_keyboard

from keyboards.inline.psych_poll_keyboards import get_requests_key, psych_poll_callback, get_ages_key, language_markup, \
    confirm_inline_keyboard, pay_callback, pay_keyboard, pre_poll_callback, pre_poll_keyboard
from keyboards.inline.start_keyboard import start_callback, get_start_markup
from keyboards.inline.verification_keyboard import get_verification_keyboard
from loader import dp, pool, verification_channel_id, list_requests, list_ages, list_languages, admins
from states.psychs_state import Psychs_form, PrePoll, EditCv


@dp.callback_query_handler(start_callback.filter(ind="psych_reg"), state="*")
async def zero_q(call : CallbackQuery):
    await PrePoll.S1.set()
    await call.message.answer('''
Добрий день.

Ви зайшли у меню для Психологів

Заповнюючи анкету (натискаючи кнопку "Далі") Ви погоджуєтесь на правила користування.
Весь опис правил Ви знайдете за командою /info

Деякі послуги платні, Тарифи та умови оплат Ви знайдете за командою /info''', reply_markup=pre_poll_keyboard)


@dp.callback_query_handler(pre_poll_callback.filter(to="poll"), state= PrePoll.S1)
@dp.callback_query_handler(psych_poll_callback.filter(level="-1"))
async def first_q(call: CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        if callback_data["@"] == "pre_poll":
            await state.reset_state(with_data=False)
            data.update(requests_list=[])

    try:
        await call.message.answer(text=
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
10. Фізичний біль''', reply_markup=await get_requests_key(data["requests_list"]))
    except MessageNotModified as exc:
        print(exc)



@dp.callback_query_handler(psych_poll_callback.filter(level="1", con=''), state = [None, EditCv.EditReqList])
@dp.callback_query_handler(psych_poll_callback.filter(level="2", con=''), state = [None, EditCv.EditAgeList])
async def react_req(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()

    key, key2 = ("requests_list", "req_id") if callback_data["level"] == "1" else ("ages_list", "age_id")

    markup = call.message.reply_markup

    async with state.proxy() as data:
        ind = int(callback_data[key2]) - 1
        if callback_data["req_id"] not in data[key]:
            markup.inline_keyboard[ind][0].text = markup.inline_keyboard[ind][0].text.replace("❌", "✅")
            data[key].append(callback_data[key2])
        else:
            markup.inline_keyboard[ind][0].text = markup.inline_keyboard[ind][0].text.replace("✅", "❌")
            data[key].remove(callback_data[key2])
    try:
        await call.message.edit_reply_markup(markup)
    except MessageNotModified as exc:
        print(exc)

@dp.callback_query_handler(psych_poll_callback.filter(level="-2"))
@dp.callback_query_handler(psych_poll_callback.filter(level="1", con="1"))
async def third_q(call: CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        if callback_data["level"] == "1":
            data["requests_list"] = sorted(data["requests_list"], key=int)
            data.update(ages_list=[])
        await call.message.edit_text(text='''Допустимий вік клієнтів⬇️''', reply_markup=await get_ages_key(data["ages_list"]))


@dp.callback_query_handler(psych_poll_callback.filter(level="2", con="1"))
async def fourth_q(call:CallbackQuery, state : FSMContext):
    async with state.proxy() as data:
        data["ages_list"] = sorted(data["ages_list"], key=int)
    await call.message.edit_text(text='''Яка Ваша мова спілкування? ⬇️''', reply_markup=language_markup)


@dp.message_handler(text="Назад", state=Psychs_form.Q1)
async def go_b(message:Message, state : FSMContext):
    await state.reset_state(with_data=False)
    await message.answer(text='''Яка Ваша мова спілкування? ⬇️''', reply_markup=language_markup)

@dp.callback_query_handler(psych_poll_callback.filter(level="3"))
async def first_q(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(callback_data)
    await Psychs_form.Q1.set()
    await call.message.answer(f'''Напишіть Ваше прізвище, ім'я, по батькові''', reply_markup=back_keyboard)

@dp.message_handler(text="Назад", state=Psychs_form.Q2)
async def qqq(message: Message):
    await Psychs_form.Q1.set()
    await message.answer(f'''Напишіть Ваше прізвище, ім'я, по батькові''', reply_markup=back_keyboard)

@dp.message_handler(text="Назад", state=Psychs_form.Q3)
@dp.message_handler(state=Psychs_form.Q1)
async def sixth_q(message: Message, state : FSMContext):
    if message.text != "Назад":
        await state.update_data(pib=message.html_text)
    await Psychs_form.Q2.set()
    await message.answer(text="Напишіть про себе 2-3 речення\nЇх будуть бачити люди під час вибору психолога.\n\n<b>Максимальна кількість символів: 350</b>", reply_markup=back_keyboard)


@dp.message_handler(text="Назад", state=Psychs_form.Q4)
@dp.message_handler(state=Psychs_form.Q2)
async def seven_q(message:Message, state : FSMContext):
    if len(message.text)>350 and message.text!="Назад":
        await message.answer(f"Кількість символів в описі більша ніж 350. Напишіть коротший опис.\n\nКількість знаків в вашому описі: {len(message.text)}")
        return
    if message.text != "Назад":
        await state.update_data(description=message.html_text)
    await Psychs_form.Q3.set()
    await message.answer(text="Надішліть ваше фото\nЙого будуть бачит люди під час вибору психолога")

@dp.message_handler(text="Назад", state=Psychs_form.Q5)
@dp.message_handler(content_types=ContentTypes.PHOTO,state=Psychs_form.Q3)
async def nine_q(message: Message, state : FSMContext):
    if message.text != "Назад":
        await state.update_data(photo_file_id = message.photo[-1].file_id)
    await Psychs_form.Q4.set()
    await message.answer("Надайте посилання на ваші інші соц. мережі (instagram, facebook)")

@dp.message_handler(text="Назад", state=Psychs_form.Price)
@dp.message_handler(state=Psychs_form.Q4)
async def nine_q(message: Message, state : FSMContext):
    if message.text != "Назад":
        await state.update_data(soc_media_url = message.text, document_urls = [], document_file_ids = [], photo_file_ids = [])
    await Psychs_form.Q5.set()
    await message.answer("<b>Завантажте документи</b> (або надайте посилання на них) підтверджуючі ваше навчання у сфері психології.\n\nнатисніть 'Далі' щоб перейти на наступний крок",
                         reply_markup=forward_back_keyboard)

@dp.message_handler(text="Назад", state=Psychs_form.Q6)
@dp.message_handler(text = "Далі", state=Psychs_form.Q5)
async def secret_4(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data["document_file_ids"] and not data["document_urls"] and not data["photo_file_ids"]:
        await message.answer("Ви не додали жодного документу")
        return
    await Psychs_form.Price.set()
    await message.answer("Введіть ціну консультації у грн\nНаприклад: 400")

@dp.message_handler(content_types=ContentTypes.TEXT, state=Psychs_form.Q5)
async def ten_q(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.entities:
            for entity in message.entities:
                if entity.type == 'url':
                    data["document_urls"].append(entity.get_text(message.text))
            await message.answer(text='Документи успішно додано')
            return
    await message.answer(text="Посилання не виявлено")

@dp.message_handler(content_types=ContentTypes.DOCUMENT, state=Psychs_form.Q5)
async def ten_q(message: Message, state : FSMContext):
    async with state.proxy() as data:
        data["document_file_ids"].append(message.document.file_id)

    await message.reply(text='Документ успішно додано')

@dp.message_handler(content_types=ContentTypes.PHOTO, state=Psychs_form.Q5)
async def ten_q(message: Message, state : FSMContext):
    async with state.proxy() as data:
        data["photo_file_ids"].append(message.photo[-1].file_id)

    await message.reply(text='Фото успішно додано')

@dp.message_handler(state=Psychs_form.Q5)
async def ten_q(message: Message):
    await message.answer(text='Документ можно завантажити тільки у вигляді файлу або скинути посилання на нього')


@dp.message_handler(text="Назад", state=Psychs_form.Q7)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Psychs_form.Price)
async def twelve_q(message : Message, state : FSMContext):
    if message.text != "Назад":
        try:
            await state.update_data(price = int(message.text))
        except ValueError:
            await message.answer("Ціну не було виявлено, введіть лише число")
            return
    await Psychs_form.Q6.set()
    await message.answer(
'''Надайте відповіді на питання-приклади (пункт потрібний для веріфікації )


а) що ви зробите, якщо Ви не в змозі допомогти клієнту, або клієнт не йде на контакт, тобто ви не справляетесь і стан клієнта погіршується?
б) ваші перші дії/ слова, коли людина знаходиться у стані емоційного зриву?
в) чи готові ви працювати з людьми які отримали поранення. З чого будете починати діалог?
(вкажіть, якщо не готові працювати з такими людьми, але перед тим вам потрібна консультація в цьому питанні)''', reply_markup=back_keyboard)


@dp.callback_query_handler(pay_callback.filter(level="0"),state=Psychs_form.Q7)
async def seven_q(call:CallbackQuery):
    await call.answer()
    await Psychs_form.Q7.set()
    await call.message.answer(text="Поділіться Вашим номером телефону⬇️"
                        "\n\n<b>Це необхідно для можливості зв'язатись з вами якщо у вас немає юзернейму в телеграмі</b>", reply_markup=request_contact_markup)

@dp.message_handler(state=Psychs_form.Q6)
async def seven_q(message:Message, state : FSMContext):
    await state.update_data(answers=message.html_text)
    await Psychs_form.Q7.set()
    await message.answer(text="Поділіться Вашим номером телефону⬇️"
                         "\n\n<b>Це необхідно для можливості зв'язатись з вами якщо у вас немає юзернейму в телеграмі</b>", reply_markup=request_contact_markup)

@dp.callback_query_handler(pay_callback.filter(level="-1"), state='*')
async def eleven_q_2(call : CallbackQuery, state : FSMContext):
    data = await state.get_data()

    competences = "\n"
    for competence in data["requests_list"]:
        competences += list_requests[str(competence)] + "\n"

    ages = ""
    for age in data["ages_list"]:
        ages += list_ages[str(age)] + ", "

    if data["document_urls"]:
        documents = "\n"
        for ind, doc in enumerate(data["document_urls"], 1):
            documents += str(ind) + doc + "\n"

    if data["document_file_ids"]:
        media = MediaGroup()
        for doc in data["document_file_ids"]:
            media.attach_document(document=doc)
        await call.message.answer_media_group(media=media)

    if data["photo_file_ids"]:
        media2 = MediaGroup()
        for photo in data["photo_file_ids"]:
            media2.attach_photo(photo=photo)
        await call.message.answer_media_group(media=media2)

    text = f'''
Анкета:

{f"Юзернейм: @{call.from_user.username}" if call.from_user.username is not None else ""}

ПІБ: {data["pib"]}\n
Запити: {competences}
Вік людей: {ages[:-2]}

Мова: {list_languages[str(data["language"])]}
Соц мережі: {data["soc_media_url"]}

Умови роботи: {"З оплатою та без оплати" if data["pay_variant"] == 1 else "З оплатою + термінова допомога" if data["pay_variant"] == 2 else "Тільки з оплатою"}
Номер телефону: {data["phone_number"] if data["phone_number"] is not None else "Не вказано"}
{("Посилання на документи:" + documents) if data["document_urls"] else ""}


Про себе:
{data['description']}'''

    await call.message.answer_photo(photo=data["photo_file_id"], caption=text)

    await call.message.answer("Внизу ваші дані, перевірте чи ви все заповнили правильно\n\n(Клієнт буде бачити тільки деякі з цих данних)", reply_markup=confirm_inline_keyboard)


@dp.message_handler(text = 'Не ділитись номером телефону',state=Psychs_form.Q7)
@dp.message_handler(content_types=ContentTypes.CONTACT,state=Psychs_form.Q7)
async def eleven_q(message : Message, state : FSMContext):
    if message.contact:
        await state.update_data(phone_number = message.contact.phone_number)

    data = await state.get_data()

    competences = "\n"
    for competence in data["requests_list"]:
        competences += list_requests[str(competence)] + "\n"

    ages = ""
    for age in data["ages_list"]:
        ages += list_ages[str(age)] + ", "

    if data.get("document_urls") :
        documents = "\n"
        for ind, doc in enumerate(data["document_urls"], 1):
            documents += str(ind) + ". " + doc + "\n"

    if data.get("document_file_ids"):
        media = MediaGroup()
        for doc in data["document_file_ids"]:
            media.attach_document(document=doc)
        await message.answer_media_group(media=media)

    if data["photo_file_ids"]:
        media2 = MediaGroup()
        for photo in data["photo_file_ids"]:
            media2.attach_photo(photo=photo)
        await message.answer_media_group(media=media2)

    text = f'''
Анкета:

{f"Юзернейм: @{message.from_user.username}" if message.from_user.username is not None else ""}
    
ПІБ: {data["pib"]}\n
Запити: {competences}
Вік людей: {ages[:-2]}
    
Мова: {list_languages[str(data["language"])]}
Соц мережі: {data["soc_media_url"]}
    
Номер телефону: {data["phone_number"] if data.get("phone_number") else "Не вказано"}
{("Посилання на документи:" + documents) if data.get("document_urls") else ""}
    
    
Про себе:
{data['description']}'''

    await message.answer_photo(photo=data["photo_file_id"], caption = text, reply_markup=ReplyKeyboardRemove())

    await message.answer("Зверху ваші дані, перевірте чи ви все заповнили правильно\n\n(Клієнт буде бачити тільки деякі з цих данних)", reply_markup=confirm_inline_keyboard)


@dp.callback_query_handler(pay_callback.filter(level="1"), state=Psychs_form.Q7)
async def fifth_q(call:CallbackQuery):
    await call.message.edit_text(text='''
Користування платформою коштує 300грн/місяць.

<b>Перша консультація для клієнта - безкоштовна.
Далі Ви з клієнтом обговорюєте вартість на наступні зустрічі.</b>

Підтвердіть, що приймаєте дані умови.''', reply_markup=pay_keyboard)


@dp.callback_query_handler(pay_callback.filter(level="2"), state=Psychs_form.Q7)
async def fifth_q(call:CallbackQuery, callback_data : dict, state : FSMContext):
    await state.update_data(callback_data)
    amount = 300_00

    if call.from_user.id in admins:
        amount = int(amount/100)

    await dp.bot.send_invoice(chat_id=call.message.chat.id, title='Оплата за реєстрацію', description='Оплатіть реєстрацію', payload=callback_data["pay_variant"],
                              provider_token=PROVIDER_TOKEN, currency='UAH', prices=[LabeledPrice(label='Оплата за реєстрацію', amount=amount)],
                              protect_content=True)


@dp.pre_checkout_query_handler(state='*')
async def secret_2(query: PreCheckoutQuery):
    await dp.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT, state=Psychs_form.Q7)
async def secret_4(message: Message, state: FSMContext):
    await Psychs_form.Price.set()
    data = await state.get_data()
    async with pool.acquire() as conn:

        sql = f'''insert into psychs(user_id, username, pib, competence, ages, language, pay_variant, phone_number, description, photo_file_id, date_of_expiration, date_of_registration, price) values
                ({message.from_user.id}, '{message.from_user.username}', '{data["pib"].replace("'", "''")}', ARRAY{sorted(data["requests_list"], key=int)}::int[], ARRAY{sorted(data["ages_list"], key=int)}::int[], {data["language"]},{data["pay_variant"]},
                '{data.get("phone_number")}','{data["description"].replace("'", "''")}', '{data["photo_file_id"]}', '2222-12-03'::date,'{date.today()}'::date, {data.get("price", "'None'")}) returning *'''.replace(
                "'None'", "null")

        data_2 = await conn.fetchrow(sql)

    new_message = await message.answer("Дякую", reply_markup=ReplyKeyboardRemove())
    await new_message.delete()

    await message.answer('''
Дякуємо, реєстрацію було завершено ✅

Після того як Ваша анкета пройде верифікацію її зможуть бачити клієнти.

ВАЖЛИВО 👉Ви можете вимикати/вмикати анкету в залежності чи можете брати нових клієнтів.

Долучайтесь до важливих груп
🔔 група запитів «Термінова допомога» https://t.me/+hBNqjZoJYZRkZmYy


⚙️ група психологів по орг.питанням - https://t.me/+Gg8ek5gCvUs4NjQy


📨 надіслати пост-пораду для публікації в нащих соц.мережах - https://t.me/marina_mindbody


👥 наші соц.мережі 
https://instagram.com/mind_body_help
https://t.me/mind_body_help
https://facebook.com/102883732466124/''')
    await message.answer("Хто ви?", reply_markup=await get_start_markup(message.from_user.id))


    await dp.bot.send_message(text='⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️', chat_id=verification_channel_id)

    competences = "\n"
    for competence in data_2["competence"]:
        competences += list_requests[str(competence)] + "\n"

    ages = ""
    for age in data_2["ages"]:
        ages += list_ages[str(age)] + ", "

    if data.get("document_urls"):
        documents = "\n"
        for ind, doc in enumerate(data["document_urls"], 1):
            documents += str(ind) + ". " + doc + "\n"

    if data.get("document_file_ids"):
        media = MediaGroup()
        for doc in data["document_file_ids"]:
            media.attach_document(document=doc)
        await dp.bot.send_media_group(media=media, chat_id=verification_channel_id)

    if data["photo_file_ids"]:
        media2 = MediaGroup()
        for photo in data["photo_file_ids"]:
            media2.attach_photo(photo=photo)
        await dp.bot.send_media_group(media=media2, chat_id=verification_channel_id)

    n = "\n"
    text = f'''
Анкета:

ПІБ (тг): {message.from_user.get_mention(as_html=True)}
{f"Юзернейм: @{message.from_user.username}" if message.from_user.username is not None else ""}

ПІБ: {data_2["pib"]}\n
Ціна констультації: {str(data["price"]) + " грн" if data_2["price"] else "без оплати"}

Запити: {competences}
Вік людей: {ages[:-2]}

Мова: {list_languages[str(data_2["language"])]}
Умови роботи: {"З оплатою та без оплати" if data_2["pay_variant"] == 1 else "З оплатою + термінова допомога" if data_2["pay_variant"] == 2 else "Тільки з оплатою"}
Номер телефону: {data_2["phone_number"] if data_2["phone_number"] is not None else "Не вказано"}
{("Посилання на документи:" + documents) if data.get("document_urls") else ""}


Про себе:
{data_2['description']}'''

    await dp.bot.send_message(chat_id=verification_channel_id, text=f"Відповіді на питання: {data['answers']}")
    await dp.bot.send_photo(chat_id=verification_channel_id, photo=data["photo_file_id"], caption=text,
                            reply_markup=await get_verification_keyboard(id=data_2["id"]))
    await state.reset_state(with_data=True)



