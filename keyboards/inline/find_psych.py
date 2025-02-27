from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.start_keyboard import start_callback, to_menu_callback
from loader import  list_requests, list_ages, list_languages


find_psych_callback = CallbackData("find","level", "req_id", "age_id", "language", "pay","choice", "con")

def make_find_psych_callback(level, req_id = '0', age_id = 0, language = 0, pay = 0, choice = 0, con = ''):
    return find_psych_callback.new(level=level, req_id=req_id, age_id=age_id,language=language, pay=pay,choice = choice, con=con)

async def get_requests2_keyboard(requests_list):
    markup = InlineKeyboardMarkup(row_width=1)
    for key, value in list_requests.items():
        markup.row(InlineKeyboardButton(text=value + "   " + ("✅" if key in requests_list else "❌"), callback_data=make_find_psych_callback(level="1", req_id=key)))
    markup.row(InlineKeyboardButton(text="Далі", callback_data=make_find_psych_callback(level='1',con='1')))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=to_menu_callback.new()))
    return markup


async def get_ages_key_2():
    markup = InlineKeyboardMarkup(row_width=1)
    for key, value in list_ages.items():
        markup.row(InlineKeyboardButton(text=value, callback_data=make_find_psych_callback(level='2',age_id=key)))

    markup.row(InlineKeyboardButton(text="Назад", callback_data=start_callback.new(ind="2")))
    return markup


async def get_language_key_2(callback_data : dict):
    markup = InlineKeyboardMarkup(row_width=1)
    for key, value in list_languages.items():
        markup.row(InlineKeyboardButton(text=value, callback_data=make_find_psych_callback(level='3', age_id=callback_data["age_id"], language=key)))

    markup.row(InlineKeyboardButton(text="Назад", callback_data=make_find_psych_callback(level='1', con='1')))
    return markup

async def get_work_condition_key_2(callback_data : dict):
    markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=
    [
        [InlineKeyboardButton(text="Перша зустріч без оплати (45 хв)", callback_data=make_find_psych_callback(
            level='4',age_id = callback_data["age_id"], language=callback_data["language"], pay=1))],
        [InlineKeyboardButton(text="Платно за домовленністю",callback_data=make_find_psych_callback(
            level='4',age_id = callback_data["age_id"], language=callback_data["language"], pay=2))],
        [InlineKeyboardButton(text="Назад", callback_data=make_find_psych_callback(level='2',age_id=callback_data["age_id"]))]
    ])

    return markup


async def get_psych_find_key_2(callback_data: dict):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Знайти іншого", callback_data=make_find_psych_callback(
            level='5', age_id = callback_data["age_id"], language=callback_data["language"], pay=callback_data["pay"], choice = 1))],
        [InlineKeyboardButton(text="Дякую, цей психолог мені підходить", callback_data=make_find_psych_callback(
            level='5', age_id = callback_data["age_id"], language=callback_data["language"], pay=callback_data["pay"], choice=2))],
        [InlineKeyboardButton(text="Назад", callback_data=make_find_psych_callback(
            level='5', age_id = callback_data["age_id"], language=callback_data["language"], pay=callback_data["pay"], choice=3))]
    ])
    return markup

to_pre_poll_user_keyboard = InlineKeyboardMarkup( inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=start_callback.new(ind = '2'))],
] )
