from aiogram.types import AllowedUpdates

from loader import scheduler, scheduler2
from utils.misc.reminder import remind

from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await set_default_commands(dp)



if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    scheduler2.add_job(remind, trigger='cron', hour='9')
    scheduler2.start()
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, allowed_updates=AllowedUpdates.all(), skip_updates=True)



