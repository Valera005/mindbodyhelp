import logging

from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from loader import dp, exceptions_chat_id


@dp.errors_handler(exception=MessageNotModified)
async def errors_hand(update:types.Update, exception :KeyError):
    return True


@dp.errors_handler()
async def errors_hand(update:types.Update, exception :KeyError):
    if exception.__str__()=="Message to delete not found":
        return

    chat_id = None

    state = dp.current_state()
    await state.reset_state(with_data=True)

    if update.callback_query:
        user = update.callback_query.from_user
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        user = update.message.from_user
        chat_id= update.message.chat.id

    if chat_id:
        await dp.bot.send_message(chat_id=chat_id, text="Виникла непердбачувана помилка, спробуйте ввести /menu і повторити свої дії"
                                  "\nПри повторному виниканні зверніться до @ValeraK"
                                  f"\n\nПомилка: {exception}")
        await dp.bot.send_message(chat_id=exceptions_chat_id, text=f'MindBodyHelp Виникла помилка у {user.get_mention(as_html=True)}:\n\n{exception}')
