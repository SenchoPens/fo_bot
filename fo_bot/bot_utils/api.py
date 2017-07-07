from logging import getLogger

from requests import get, RequestException


logger = getLogger(__name__)


class APIMethodException:
    """Represents exception during calling a method"""

    def __init__(self, message, code, text):
        self.message = message
        self.code = code
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
            raise APIMethodException(f'Request to API ended up with error status code {res.status_code}',
                                     res.status_code, res.json()['message']) from e
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
