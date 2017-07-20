from typing import Dict

from requests import RequestException


class EGRNError(RequestException):
    """Represents exception during calling an API method"""

    def __init__(self, message, code, text):
        super().__init__(message)
        self.code = code
        self.text = text


class APIObject:
    def __init__(self, json: Dict):
        if not json:
            raise EGRNError(f'Server responce is empty')
        self.errors = json['error']
        if self.errors:
            raise EGRNError(f'`errors` field in server responce is not empty: {self.errors}',
                            self.errors['code'], self.errors['mess'])