import os

from enum import IntEnum, auto


# Telegram API
BOT_TOKEN = os.environ['BOT_TOKEN']
MAX_DATA_LEN = 64

# Bot
#  \                        __________
#   \         __           /_        _\       __
#    \       /  \         /  \      /  \     /  \
END, ASK_PHONE, FETCH_PHONE, REGISTER, CABINET, ORDER = range(-1, 5)

CONVERSATION_DUMP_FILENAME = 'bot_user_conversations.pickle'
USER_DATA_DUMP_FILENAME = 'bot_user_data.pickle'

TYPES = [{'text': 'Электронная выписка ЕГРН (250р.)', 'id': 10},
         ]


class Prefix(IntEnum):
    FULL_DATA = auto()
    ORDER_TYPE = auto()


API_TOKEN = os.environ['API_TOKEN']
API_URL = 'http://findtheowner.ru/api/v0.php'

ROSREEST_API_TOKEN = os.environ['ROSREESTR_API_TOKEN']

GMAPS_API_TOKEN = os.environ['GMAPS_API_TOKEN']

LIST_OF_ADMINS = os.environ['ADMINS'].split(':')

REQUEST_KWARGS={
    'proxy_url': 'socks5://112.133.225.56:9999',
    # Optional, if you need authentication:
    # 'urllib3_proxy_kwargs': {
        # 'username': 'PROXY_USER',
        # 'password': 'PROXY_PASS',
    # }
}
