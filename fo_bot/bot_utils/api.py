from logging import getLogger

from requests import get, RequestException


logger = getLogger(__name__)


class APIMethodException(RequestException):
    """Represents exception during calling a method"""

    def __init__(self, message, code, text):
        super().__init__(message)
        self.code = code
        self.text = text


class APIMethod:
    _url = 'http://findtheowner.ru/api/v0.php'
    def __init__(self, method, token):
        self._method = method
        self._token = token

    def __call__(self, **kwargs):
        res = get(self._url, params={'token': self._token, 'class': self._method, **kwargs})

        try:  # Probably there is a better way to raise from
            res.raise_for_status()
        except RequestException as e:
            logger.warning(f'Request error: {res.status_code}. Request URL: {res.url}. Request text: {res.text}')
            raise APIMethodException(f'Something bad with request: {res.status_code}',
                                     res.status_code, e.response) from e

        res_json = res.json()
        api_err_code = int(res_json.get('error', False))
        if api_err_code:
            raise APIMethodException(f'Request to API ended up with error status code {api_err_code}',
                                     api_err_code, res_json['message'])

        return res_json


class API:
    def __init__(self, token):
        self._token = token

    def __getattr__(self, item):
        logger.debug('API Method call {item}')
        return APIMethod(item, token=self._token)


def main():
    from ..settings import API_TOKEN
    t = API(API_TOKEN)
    t.balance(phone='9263793151')


if __name__ == '__main__':
    main()
