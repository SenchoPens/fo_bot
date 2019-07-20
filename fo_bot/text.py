from typing import NamedTuple


class Name(NamedTuple):
    rus: str
    eng: str

    def get_pretty(self):
        return '«' + self.rus + '»'


class ActionName:
    start = Name(rus='Начать', eng='start')
    show_balance = Name(rus='Баланс', eng='balance')
    end = Name(rus='Завершить', eng='end')
    cancel = Name(rus='Отменить', eng='cancel')
    show_help = Name(rus='Помощь', eng='help')
    auth = Name(rus='Авторизоваться', eng='auth')
    register = Name(rus='Зарегистрироваться', eng='register')
    change_cost = Name(rus='Изменить стоимость выписки', eng='change_cost')
    recharge = Name(rus='Пополнить', eng='recharge')
    search = Name(rus='Искать', eng='search')
    count_saving = Name(rus='Налог', eng='count')
