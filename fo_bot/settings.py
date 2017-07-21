from enum import IntEnum, auto
# Telegram API
BOT_TOKEN = '342476710:AAG0fW1kmSiAYCbNl-IlzjmN8VjJK9aRt5w'
MAX_DATA_LEN = 64

# Bot
#  \                        __________
#   \         __           /_        _\       __
#    \       /  \         /  \      /  \     /  \
END, ASK_PHONE, FETCH_PHONE, REGISTER, CABINET, ORDER = range(-1, 5)
#
CONVERSATION_DUMP_FILENAME = 'bot_user_conversations.pickle'
USER_DATA_DUMP_FILENAME = 'bot_user_data.pickle'

TYPES = [{'text': 'Электронная выписка ЕГРН (250р.)', 'id': 10},
         ]


class Prefix(IntEnum):
    FULL_DATA = auto()
    ORDER_TYPE = auto()


API_TOKEN = 'D5E43FGD7A3E63E57443B54112D4'
API_URL = 'http://findtheowner.ru/api/v0.php'

ROSREEST_API_TOKEN = '9AEE-ZLJY-QJAN-DXF7'

GMAPS_API_TOKEN = 'AIzaSyBAV7blDSrOsKuuX2426O5U0tzPQEcs0Cw'
