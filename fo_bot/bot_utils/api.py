from logging import getLogger

from requests import get, RequestException


logger = getLogger(__name__)


class APIMethodException(RequestException):
    """Represents exceptio during calling a method"""


class APIMethod:
    def __init__(self, url):
        self._url = url

    def __call__(self, **kwargs):
        res = get(self._url, params=kwargs)
        raise APIMethodException from res.raise_for_status()
        return res.json()


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
