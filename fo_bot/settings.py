import os

from enum import IntEnum, auto


# Telegram API
BOT_TOKEN = os.environ['BOT_TOKEN']
MAX_DATA_LEN = 64

END, FETCH_PHONE, REGISTER, MAIN, ORDER, RECHARGE = range(-1, 5)

OVERSEERS_PHONES = os.environ['OVERSEERS_PHONES'].split(':')

VALUER, ADMIN, OVERSEER = range(3)
USER_ACCESS_FILENAME = 'user_access.shelve'


class CallbackPrefix(IntEnum):
    FULL_DATA = auto()
    ORDER_TYPE = auto()
    DOC_TYPE = auto()


API_TOKEN = os.environ['API_TOKEN']
API_URL = 'https://findtheowner.ru/api'

ROSREEST_API_TOKEN = os.environ['ROSREESTR_API_TOKEN']

GMAPS_API_TOKEN = os.environ['GMAPS_API_TOKEN']

REQUEST_KWARGS = {
    # socks5://address:port
    'proxy_url': os.environ.get('PROXY_URL', None),
    'urllib3_proxy_kwargs': {
        'username': os.environ.get('PROXY_USERNAME', None),
        'password': os.environ.get('PROXY_PASSWORD', None),
    }
}
