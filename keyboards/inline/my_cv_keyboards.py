from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.psych_poll_keyboards import get_psych_poll_callback
from keyboards.inline.start_keyboard import start_callback
from loader import list_requests, list_ages

my_cv_callback = CallbackData("my_cv", "id")
confirmation_callback = CallbackData("conf","choice")

async def get_my_cv_key(status : bool):
    text_1 = "Статус: Включена ✅" if status else "Статус: Виключена ❌"

    my_cv_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text_1, callback_data=my_cv_callback.new(id=1))],
        [InlineKeyboardButton(text="Змінити анкету", callback_data=my_cv_callback.new(id=2))],
        [InlineKeyboardButton(text="Назад", callback_data=my_cv_callback.new(id=0))]
    ])
    return my_cv_keyboard


confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Так", callback_data=confirmation_callback.new(choice="1"))],
    [InlineKeyboardButton(text="Ні", callback_data=confirmation_callback.new(choice="0"))],
])



edit_cv_callback = CallbackData("edit","thing", "to")

def get_edit_cv_callback(thing = '', to = ''):
    return edit_cv_callback.new(thing=thing, to=to)



def get_things_keyboard():
    things_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Запити, з якими ви працюєте", callback_data=get_edit_cv_callback("req"))],
        [InlineKeyboardButton(text="Вік людей, з якими ви працюєте", callback_data=get_edit_cv_callback("age"))],
        [InlineKeyboardButton(text="Юзернейм у телеграм", callback_data=get_edit_cv_callback("username"))],
        [InlineKeyboardButton(text="Фото", callback_data=get_edit_cv_callback("photo"))],
        [InlineKeyboardButton(text="Номер телефону", callback_data=get_edit_cv_callback("phone_number"))],
        [InlineKeyboardButton(text="Ціна консультації", callback_data=get_edit_cv_callback("price"))],
        [InlineKeyboardButton(text='Розділ "про себе"', callback_data=get_edit_cv_callback("description"))],
        [InlineKeyboardButton(text='Видалити анкету', callback_data=get_edit_cv_callback("delete_cv"))],
        [InlineKeyboardButton(text='Назад', callback_data=start_callback.new(ind="0"))]])
    return things_keyboard

universal_confirmation_callback = CallbackData("conf4", "where", "choice")

delete_my_cv_confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Так", callback_data = universal_confirmation_callback.new(where = "delete_my_cv", choice = "1"))],
    [InlineKeyboardButton(text="Назад", callback_data = get_edit_cv_callback(to="back"))]
])


async def get_edit_requests_key(requests_list):
    markup = InlineKeyboardMarkup(row_width=1)

    for key, value in list_requests.items():
        markup.row(InlineKeyboardButton(text=value + "   " + ("✅" if key in requests_list else "❌"), callback_data= get_psych_poll_callback(level="1", req_id=key)))

    markup.row(InlineKeyboardButton(text="Далі", callback_data=get_edit_cv_callback(to='finish_req')))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=get_edit_cv_callback(to='back')))
    return markup

async def get_edit_ages_key(ages_list):
    markup = InlineKeyboardMarkup(row_width=1)

    for key, value in list_ages.items():
        markup.row(InlineKeyboardButton(text=value + "   " + ("✅" if key in ages_list else "❌"), callback_data= get_psych_poll_callback(level="2", age_id=key)))

    markup.row(InlineKeyboardButton(text="Далі", callback_data=get_edit_cv_callback(to='finish_age')))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=get_edit_cv_callback(to='back')))
    return markup

edit_cv_go_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=get_edit_cv_callback(to='back'))]
])