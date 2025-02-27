from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

request_contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,keyboard=[
    [KeyboardButton(text="Поділитись номером телефону",request_contact=True)],
    [KeyboardButton(text="Не ділитись номером телефону")],
    [KeyboardButton(text="Назад")]
])

request_contact_markup_2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,keyboard=[
    [KeyboardButton(text="Поділитись номером телефону",request_contact=True)],
    [KeyboardButton(text="Назад")]
])

back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Назад")]])

forward_back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Далі")],[KeyboardButton(text="Назад")]], one_time_keyboard=True)