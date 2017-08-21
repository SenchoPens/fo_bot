from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.bot_states.cabinet import cabinet_help
from fo_bot import logger, api


def make_cabinet(bot, update, user_data):
    user_data['logged'] = True
    if user_data.get('orders', None) is None:
        user_data['orders'] = []
    cabinet_help(bot, update)


@api_error_handler(END)
def auth(bot, update, user_data):
    api.auth(phone=user_data['phone'])
    update.message.reply_text('Вы успешно авторизовались')
    update.message.reply_text(
        'Уважаемый пользователь, С моей помощью Вы можете '
        'заказать выписку ЕГРН прямо в мессенджере. '
        'Но для этого Вам надо пополнить баланс в сервисе '
        '"Узнай владельца недвижимости" на сайте www.findtheowner.ru.'
    )
    make_cabinet(bot, update, user_data)
    return CABINET
