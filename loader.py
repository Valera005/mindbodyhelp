import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2()
dp = Dispatcher(bot, storage=storage)

DB_USER = "postgres"
DB_PASS = "your_pass"
DB_NAME = "mindbodyhelp"
DB_HOST = "127.0.0.1"


loop = asyncio.get_event_loop()

pool : asyncpg.Pool= loop.run_until_complete(asyncpg.create_pool(user = DB_USER, password=DB_PASS, host = DB_HOST, database=DB_NAME, max_size=25))

list_requests = {
    "1" : "1. Панічні Атаки",
    "2" : "2. Страх за себе, за рідних",
    "3" : "3. Втома, відчай, бессилля, тривожність",
    "4" : "4. Втрата сенсів, небажання жити",
    "5" : "5. Як заспокоїтись?",
    "6" : "6. Проблема вибору",
    "7" : "7. Що говорити дітям?",
    "8" : "8. Відчуття провини, сором",
    "9" : "9. Як підтримати родичів",
    "10": "10. Фізичний біль"
}

list_ages = {
    "1" : "7-10",
    "2" : "11-16",
    "3" : "17-25",
    "4" : "26-44",
    "5" : "45-65",
    "6" : "66+"
}

list_languages = {
    "1" : "Російська",
    "2" : "Українська",
    "3" : "Обидві",
}


exceptions_chat_id = -1001730319729
fast_help_channel_id = -1001798890184
verification_channel_id = -1001470830704
feedback_channel_id = -1001646010875
scheduler = AsyncIOScheduler(jobstores={"default":RedisJobStore()})
scheduler2 = AsyncIOScheduler()


admins = [698281804, 528984687, 77435282]