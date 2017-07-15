from logging import getLogger

from requests import get, RequestException

from fo_bot.settings import *


logger = getLogger(__name__)


class APIMethodException(RequestException):
    """Represents exception during calling a method"""

    def __init__(self, message, code: int, text):
        super().__init__(message)
        self.code: int = code
        self.text = text


class APIMethod:
    def __init__(self, method):
        self._method = method

    def __call__(self, **kwargs):
        res = get(API_URL, params={'token': API_TOKEN, 'class': self._method, **kwargs})
        print(res.status_code)
        print(res.json())

        try:  # Probably there is a better way to raise from
            res.raise_for_status()
        except RequestException as e:
            logger.warning(f'Request error: {res.status_code}')
            raise APIMethodException(f'Something bad with request: {res.status_code}',
                                     res.status_code, e.response) from e

        res_json = res.json()
        api_err_code = int(res_json.get('error', False))
        if api_err_code:
            raise APIMethodException(f'Request to API ended up with error status code {api_err_code}',
                                     api_err_code, res_json['message'])

        return res_json


class API:
    def __getattr__(self, item):
        logger.debug('API Method call {item}')
        return APIMethod(item)


def main():
    t = API()
    t.balance(phone='9263793151')


if __name__ == '__main__':
    main()
