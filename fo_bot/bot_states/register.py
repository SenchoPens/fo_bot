from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.bot_states import auth
from fo_bot import api


def ask_email(bot, update):
    update.message.reply_text('Введите адрес своей электронной почты:')
    return REGISTER


@api_error_handler(END)
def register(bot, update, user_data):
    email = update.message.text
    api.register(phone=user_data['phone'], email=email)
    return auth.auth(bot, update, user_data)
