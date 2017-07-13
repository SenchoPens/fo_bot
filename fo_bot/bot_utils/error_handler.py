from functools import wraps
from logging import getLogger

from fo_bot.bot_utils.api import APIMethodException


logger = getLogger(__name__)


class api_error_handler:
    """Decorator around functions that make api requests."""

    def __init__(self, bad):
        self.bad = bad

    def __call__(self, func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            try:
                return func(bot, update, *args, **kwargs)
            except APIMethodException as e:
                if 400 <= e.code < 500:  # client error
                    err = e.text
                    update.message.reply_text(e.text)
                else:
                    err = 'Something bad'
                    update.message.reply_text('Извините, произошла какая-то ошибка. Попробуйте позже.')
                logger.warning(f'API error: "{err}" with api request by {update.effective_user.name}')
                return self.bad
        return wrapped
