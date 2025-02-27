from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.inline.find_psych import to_pre_poll_user_keyboard
from keyboards.inline.info_keyboards import to_info, to_info_keyboard
from keyboards.inline.psych_poll_keyboards import to_pre_poll_keyboard
from loader import dp
from states.psychs_state import PrePoll, PrePollUser


@dp.callback_query_handler(to_info.filter(), state=PrePoll.S1)
async def f(call:CallbackQuery):
    await call.answer()
    await call.message.edit_text('''
- контакти адміністрації: /contacts
- товари та їх повний опис: /services
- тарифи на послуги/товари: /tariffs
- Угода користувача: /oferta
- Політика конфіденційності: /privacy''', reply_markup=to_pre_poll_keyboard)

@dp.callback_query_handler(to_info.filter(), state=PrePollUser.Q1)
async def f(call:CallbackQuery):
    await call.answer()
    await call.message.edit_text('''
- контакти адміністрації: /contacts
- товари та їх повний опис: /services
- тарифи на послуги/товари: /tariffs
- Угода користувача: /oferta
- Політика конфіденційності: /privacy''', reply_markup=to_pre_poll_user_keyboard)

@dp.callback_query_handler(to_info.filter())
async def f(call:CallbackQuery, state : FSMContext):
    await call.answer()
    await state.reset_state()
    await call.message.edit_text('''
- контакти адміністрації: /contacts
- товари та їх повний опис: /services
- тарифи на послуги/товари: /tariffs
- Угода користувача: /oferta
- Політика конфіденційності: /privacy''')


@dp.message_handler(commands=["info"], state="*")
async def info_resp(message:Message, state : FSMContext):
    await state.reset_state()
    await message.answer('''
- контакти адміністрації: /contacts
- товари та їх повний опис: /services
- тарифи на послуги/товари: /tariffs
- Угода користувача: /oferta
- Політика конфіденційності: /privacy
''')


@dp.message_handler(commands=["contacts"], state="*")
async def info_resp(message:Message):
    await message.answer('''
Організатор - Марина Літвінова https://t.me/marina_mindbody
Розробник - Валерій Каспрук https://t.me/ValeraK

Назва платформи: “Mind Body Help”   
Юридична назва: “ФОП Літвінова Марина Олександрівна” (надалі Виконавець)
''', reply_markup=to_info_keyboard, disable_web_page_preview=True)

@dp.message_handler(commands=["oferta"], state="*")
async def info_resp(message:Message):
    await message.answer('''Договір оферти на надання послуг - https://docs.google.com/document/d/1cayzQpe6L20OnIRxcIGVJ1YAlP5yorN9o6dRFr7fGVY/edit?usp=sharing''', reply_markup=to_info_keyboard,
                         disable_web_page_preview=True)


@dp.message_handler(commands=["services"], state="*")
async def info_resp(message:Message):
    await message.answer('''Опис послуг - https://docs.google.com/document/d/1lYeLwOEPijoXabN3op8ssWFBlSx9KDwwasWI2O6wlLk/edit?usp=sharing''', reply_markup=to_info_keyboard,
                         disable_web_page_preview=True)

@dp.message_handler(commands=["privacy"], state="*")
async def info_resp(message:Message):
    await message.answer('''Політика конфіденційності - https://docs.google.com/document/d/1DQL8GnF8PZUSsFyskIZQuyb1_1RcMPFEPNNZD0onae0/edit?usp=sharing''', reply_markup=to_info_keyboard,
                         disable_web_page_preview=True)

@dp.message_handler(commands=["tariffs"], state="*")
async def info_resp(message: Message):
    await message.answer('''Опис тарифів  - https://docs.google.com/document/d/1CBJhSmgWPM_3TPwPL8Fve3iGWu77AFD6zElfTlQGVyQ/edit?usp=sharing''',reply_markup=to_info_keyboard,
                         disable_web_page_preview=True)