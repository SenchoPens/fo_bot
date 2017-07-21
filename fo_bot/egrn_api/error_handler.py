from functools import wraps
from logging import getLogger

from .base import EGRNError


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
            except EGRNError as e:
                if e.code == 503:
                    if e.text == 'Service is temporarily unavailable':
                        update.message.reply_text('Сервисы Росреестра времменно недоступны.'
                                                  'Пожалуйста, попробуйте позже.')
                update.message.reply_text('Извините, произошла какая-то ошибка.'
                                          'Пожалуйста, попробуйте позже.')
                logger.info(f'Error with apirosreestr request for {update.effective_user.name}: {e}')
                return self.bad
        return wrapped
