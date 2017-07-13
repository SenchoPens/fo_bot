from logging import getLogger

from requests import get, RequestException


logger = getLogger(__name__)


class APIMethodException(RequestException):
    """Represents exception during calling a method"""

    def __init__(self, message, code: int, text):
        super().__init__(message)
        self.code: int = code
        self.text = text


class APIMethod:
    def __init__(self, url):
        self._url = url

    def __call__(self, **kwargs):
        res = get(self._url, params=kwargs)
        print(res.status_code)
        print(res.json())

        try:  # Probably there is a better way to raise from
            res.raise_for_status()
        except RequestException as e:
            logger.warning(f'Request error: {res.status_code}')
            raise APIMethodException(f'Something bad with request: {res.status_code}',
                                     res.status_code, e.response) from e

        resd = res.json()
        api_err_code = int(resd.get('error', False))
        if api_err_code:
            raise APIMethodException(f'Request to API ended up with error status code {api_err_code}',
                                     api_err_code, resd['message'])

        return resd


class API:
    _root_url = 'http://findtheowner.ru/test/'
    def __getattr__(self, item):
        logger.debug('Method ')
        return APIMethod(''.join((self._root_url, item, '.php')))


def main():
    t = API()
    t.asdf()


if __name__ == '__main__':
    main()
