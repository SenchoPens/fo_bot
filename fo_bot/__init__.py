import googlemaps
import shelve

import fo_bot.egrn_api
from fo_bot.api import API
from fo_bot.settings import *
from fo_bot.pickle_helpers import load_pickle_default
from fo_bot.access import User

api = API(API_TOKEN)
rosreest_api = egrn_api.API(ROSREEST_API_TOKEN)
gmaps_api = googlemaps.Client(key=GMAPS_API_TOKEN)
user_access = shelve.open(USER_ACCESS_FILENAME)
for phone in OVERSEERS_PHONES:
    user_access[phone] = User(access_level=OVERSEER, name='', phone=phone)


__all__ = ['api', 'rosreest_api', 'gmaps_api', 'user_access']
