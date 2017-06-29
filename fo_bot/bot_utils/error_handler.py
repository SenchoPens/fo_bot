from functools import wraps
from logging import getLogger

from fo_bot.bot_utils.api import APIMethodException


logger = getLogger(__name__)


class api_error_handler:
    """Decorator around functions that make api requests, so """

    def __init__(self, bad):
        self.bad = bad

    def __call__(self, func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            try:
                return func(bot, update, *args, **kwargs)
            except APIMethodException as e:
                if APIMethodException.code == 409:  #ToDo: replace with real attrs!!!
                    err = APIMethodException.text
                    update.message.reply_text(APIMethodException.text)
                else:
                    err = 'Something bad'
                    update.message.reply_text('Извините, произошла какая-то ошибка. Попробуйте позже.')
                logger.warning(f'{err} with api request by {update.effective_user.id}')
                return self.bad
        return wrapped
