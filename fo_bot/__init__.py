import googlemaps
import shelve

from fo_bot.api import API
from fo_bot.settings import *
from fo_bot.pickle_helpers import load_pickle_default
from fo_bot.access import User

api = API(API_TOKEN)
gmaps_api = googlemaps.Client(key=GMAPS_API_TOKEN, timeout=10, retry_timeout=7)
shelve_db = shelve.open(SHELVE_FILENAME, writeback=True)
for field in ('user_access', 'saving_orders', 'chat_ids'):
    if field not in shelve_db:
        shelve_db[field] = dict()
saving_orders = shelve_db['saving_orders']
user_access = shelve_db['user_access']
chat_ids = shelve_db['chat_ids']
for phone in OVERSEERS_PHONES:
    user_access[phone] = User(access_level=OVERSEER, name='', phone=phone)


__all__ = ['api', 'gmaps_api', 'shelve_db', 'user_access', 'chat_ids', 'saving_orders']
