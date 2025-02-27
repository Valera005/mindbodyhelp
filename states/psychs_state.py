from aiogram.dispatcher.filters.state import State, StatesGroup


class Psychs_form(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()
    Price = State()


class RequestPhone(StatesGroup):
    Q1 = State()


class RequestPhone2(StatesGroup):
    Q1 = State()


class FastHelp(StatesGroup):
    S1 = State()


class PrePoll(StatesGroup):
    S1 = State()

class Pay(StatesGroup):
    S1 = State()

class Feedback(StatesGroup):
    Q1 = State()

class PrePollUser(StatesGroup):
    Q1 = State()


class EditCv(StatesGroup):
    EditReqList = State()
    EditAgeList = State()
    EditPhoto = State()
    EditDescription = State()
    EditPhoneNumber = State()
    EditPrice = State()