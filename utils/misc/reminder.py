from aiogram.utils.exceptions import BotBlocked

from keyboards.inline.refresh_sub_keyborads import refresh_sub_keyboard
from loader import pool, dp


async def remind():

    async with pool.acquire() as conn:
        sql = "select * from psychs where date_of_expiration - current_date <= 0 and (is_reminded=false or is_reminded is null) order by id;"
        data = await conn.fetch(sql)

        for user in data:
            try:
                await dp.bot.send_message(chat_id=user['user_id'], text='Термін дії вашої підписки закінчився. Ваша анкета не буде показуватися користувачам.\n'
                                                                        'Щоб продовжити підписку натисніть на кнопку знизу\n\n', reply_markup=refresh_sub_keyboard)
                await conn.execute(f'''update psychs set is_reminded = true where user_id = {user["user_id"]}''')
            except BotBlocked:
                await conn.execute(f'''update psychs set is_reminded = true where user_id = {user["user_id"]}''')

        sql = "select * from psychs where date_of_expiration - current_date = 7 order by id"
        data = await conn.fetch(sql)

        for user in data:
            await dp.bot.send_message(chat_id=user['user_id'], text='Термін дії вашої підписки закінчиться через 7 днів.\n '
                                                                    'Щоб продовжити підписку натисніть на кнопку знизу\n\n',reply_markup=refresh_sub_keyboard)
