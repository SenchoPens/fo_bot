import logging
import sys

import googlemaps

from . import bot_utils, egrn_api
from .restricted import restricted
from .text import ActionName
from .settings import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers= [logging.StreamHandler(sys.stdout),
                               logging.FileHandler('bot_log'),
                               ],
                    )
logger = logging.getLogger(__name__)

api = bot_utils.API(API_TOKEN)
rosreest_api = egrn_api.API(ROSREEST_API_TOKEN)
gmaps_api = googlemaps.Client(key=GMAPS_API_TOKEN)


__all__ = ['settings', 'bot_states', 'bot_utils', 'logger',
           'restricted', 'ActionName']
