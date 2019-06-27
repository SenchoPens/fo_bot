import os

from enum import IntEnum, auto


# Telegram API
BOT_TOKEN = os.environ['BOT_TOKEN']
MAX_DATA_LEN = 64

END, FETCH_PHONE, REGISTER, MAIN, ORDER, SET_VALUE, RECHARGE = range(-1, 6)

OVERSEERS_PHONES = os.environ['OVERSEERS_PHONES'].split(':')

#VALUER, ADMIN, OVERSEER = range(3)
VALUER, ADMIN, OVERSEER = 1, 1, 1
SHELVE_FILENAME = 'db.shelve'


class CallbackPrefix(IntEnum):
    FULL_DATA = auto()
    ORDER_TYPE = auto()
    DOC_TYPE = auto()
    COUNT_SAVINGS = auto()
    GET_VALUERS_RESULTS = auto()
    SET_VALUE = auto()
    SEND_FINAL_RESULT = auto()


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
