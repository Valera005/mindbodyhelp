from aiogram import Dispatcher

from filters.call_filt import IsInUsers, IsFromFastHelpChannel, IsFirstPsych, IsInPsychs, Payload


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsInUsers)
    dp.filters_factory.bind(IsFromFastHelpChannel)
    dp.filters_factory.bind(IsFirstPsych)
    dp.filters_factory.bind(IsInPsychs)
    dp.filters_factory.bind(Payload)