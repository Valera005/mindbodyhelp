from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.info_keyboards import to_info
from keyboards.inline.start_keyboard import to_menu_callback, start_callback
from loader import list_requests, list_ages

psych_poll_callback = CallbackData("poll", "level", "req_id","age_id","language","pay", "con")

def get_psych_poll_callback(level, req_id = '',age_id = '', language = '', pay = '', con = ''):
    return psych_poll_callback.new(level = level, req_id = req_id, age_id = age_id, language = language, pay=pay, con = con)

pre_poll_callback = CallbackData("pre_poll", "to")

to_pre_poll_keyboard = InlineKeyboardMarkup( inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=start_callback.new(ind = '2'))],
])

pre_poll_keyboard = InlineKeyboardMarkup( inline_keyboard=[
    [InlineKeyboardButton(text="/info", callback_data=to_info.new())],
    [InlineKeyboardButton(text="Далі", callback_data=pre_poll_callback.new(to="poll"))],
    [InlineKeyboardButton(text="Назад", callback_data=to_menu_callback.new())],
] )

async def get_requests_key(requests_list):
    markup = InlineKeyboardMarkup(row_width=1)

    for key, value in list_requests.items():
        markup.row(InlineKeyboardButton(text=value + "   " + ("✅" if key in requests_list else "❌"), callback_data= get_psych_poll_callback(level="1", req_id=key)))

    markup.row(InlineKeyboardButton(text="Далі", callback_data=get_psych_poll_callback(level="1", con="1")))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=to_menu_callback.new()))
    return markup



async def get_ages_key(ages_list):
    markup = InlineKeyboardMarkup(row_width=1)

    for key, value in list_ages.items():
        markup.row(InlineKeyboardButton(text=value + "   " + ("✅" if key in ages_list else "❌"), callback_data= get_psych_poll_callback(level="2", age_id=key)))

    markup.row(InlineKeyboardButton(text="Далі", callback_data=get_psych_poll_callback(level="2", con='1')))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=get_psych_poll_callback(level="-1")))
    return markup


language_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Російська", callback_data=get_psych_poll_callback(level="3", language='1'))],
    [InlineKeyboardButton(text="Українська", callback_data=get_psych_poll_callback(level="3", language='2'))],
    [InlineKeyboardButton(text="Обидві", callback_data=get_psych_poll_callback(level="3", language='3'))],
    [InlineKeyboardButton(text="Назад", callback_data=get_psych_poll_callback(level="-2"))]
])


async def get_work_condition_markup(callback_data):
    work_condition_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Лише з оплатою",callback_data=get_psych_poll_callback(level="4",language=callback_data["language"], pay="1"))],
    [InlineKeyboardButton(text="Можна й без оплати",callback_data=get_psych_poll_callback(level="4",language=callback_data["language"], pay="0"))],
    [InlineKeyboardButton(text="Назад",callback_data=get_psych_poll_callback(level="2", con="1"))]
    ])

    return work_condition_markup

pay_callback = CallbackData("pay", "level","pay_variant" ,"con")

def get_pay_callback(level, pay_variant = '', con = ''):
    return pay_callback.new(level = level, pay_variant = pay_variant, con = con)

confirm_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Далі', callback_data= get_pay_callback(level="1", con="1"))],
    [InlineKeyboardButton(text='Назад', callback_data=get_pay_callback(level="0"))]
])

pay_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Так, погоджуюсь', callback_data= get_pay_callback(level="2", pay_variant = "1"))],
    [InlineKeyboardButton(text="Назад", callback_data=get_pay_callback(level='-1'))]
])
