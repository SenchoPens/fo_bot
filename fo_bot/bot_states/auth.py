from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot import logger, api


@api_error_handler(END)
def auth(bot, update, user_data):
    api.auth(phone=user_data['phone'])
    return CABINET
