
from keyboards.inline.feedback_keyboards import get_feedback_keyboard
from loader import bot


async def send_feedback_message(chat_id, user_id, pib, order_id):
    await bot.send_message(text=f"Нещодавно Ви скористалися послугою пошуку психолога на ім'я <a href='tg://user?id={user_id}'>{pib}</a>.\n\n"
                                  "Нам дуже важливий Ваш відгук та побажання щодо роботи чат-боту та якості послуг, які Ви отримали.\n\n"
                                  "Натисніть на кнопку знизу щоб пройти опитування.\nЧас проходження: 3 хвилини\n\n"
                                  "Якщо ми були корисні для Вас, Ви можете зробити донат для розвитку платформи за посиланням https://send.monobank.ua/jar/m6dBQVKjE\n\n"
                                  "Це допоможе нам і надалі надавати швидкі послуги психологічної підтримки.",
                           reply_markup=await get_feedback_keyboard(order_id), chat_id=chat_id)
