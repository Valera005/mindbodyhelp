import datetime

from aiogram import Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery, Message

from loader import fast_help_channel_id, pool


class IsFirstPsych(BoundFilter):
    async def check(self, call : CallbackQuery) -> bool:
        return (await Dispatcher.get_current().current_state().get_data())["ind"]==0


class IsInUsers(BoundFilter):
    async def check(self, call : CallbackQuery) -> bool:
      async with pool.acquire() as conn:
        return await conn.fetchval(f'''SELECT exists (SELECT 1 FROM users WHERE user_id = {call.from_user.id} LIMIT 1)''')

class IsFromFastHelpChannel(BoundFilter):
    async def check(self, call:CallbackQuery) -> bool:
        return call.message.chat.id==fast_help_channel_id

class IsInPsychs(BoundFilter):
    async def check(self, call : CallbackQuery) -> bool:
      async with pool.acquire() as conn:
        return await conn.fetchval(f'''SELECT exists (SELECT 1 FROM psychs WHERE user_id = {call.from_user.id} LIMIT 1)''')

class Payload(BoundFilter):
    def __init__(self, payload : str):
        self.payload = payload

    async def check(self, message : Message) -> bool:
        if message.successful_payment:
            return message.successful_payment.invoice_payload == self.payload
        return False