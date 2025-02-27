from datetime import date

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from asyncpg import UniqueViolationError

from keyboards.inline.my_cv_keyboards import my_cv_callback
from keyboards.inline.start_keyboard import get_start_markup, to_menu_callback
from loader import dp, pool
from states.psychs_state import RequestPhone


@dp.message_handler(CommandStart(), state = "*")
async def bot_start(message: types.Message, state : FSMContext):
    async with pool.acquire() as con:
        try:
            args = message.get_args()
            await con.execute(
                f'''insert into raw_users(name,user_id,username, deeplink, date_of_registration) values ('{message.from_user.full_name.replace("'", "''")}',{message.from_user.id}, '{message.from_user.username}',
            '{args if args else None}','{date.today().strftime('%Y-%m-%d')}'::date )'''.replace("'None'", 'null'))
        except UniqueViolationError:
            pass

    await state.reset_state(with_data=True)
    await message.answer(text='''
Добрий день, Вас вітає бот пошуку психологічної допомоги.
Будь ласка, заповніть анкету і ми надішлемо Вам контакти людини, яка відповідає Вашому запиту.

Якщо Вам потрібна Термінова психологічна допомога, натисніть відповідну кнопку з позначкою 🔔 і черговий психолог Вам відповість. 

Якщо виникли запитання, будь ласка, напишіть мені @marina_mindbody''')
    await message.answer(text="Хто Ви?", reply_markup=await get_start_markup(message.from_user.id))

@dp.message_handler(commands='menu', state = "*")
async def bot_start(message: types.Message, state : FSMContext):
    await state.reset_state(with_data=True)
    await message.answer(text="Хто Ви?", reply_markup=await get_start_markup(message.from_user.id))


@dp.callback_query_handler(to_menu_callback.filter(), state="*")
async def bot_start_2(call:types.CallbackQuery, state : FSMContext):
    await state.reset_state(with_data=True)

    await call.message.edit_text(text="Хто Ви?", reply_markup=await get_start_markup(call.from_user.id))

@dp.callback_query_handler(my_cv_callback.filter(id="0"))
async def bot_start_3(call:types.CallbackQuery, state : FSMContext):
    await state.reset_state(with_data=True)

    await call.message.delete()
    await call.message.answer(text="Хто Ви?", reply_markup=await get_start_markup(call.from_user.id))


