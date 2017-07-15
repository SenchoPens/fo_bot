from typing import Dict


class EGRNError(Exception):
    pass


class APIObject:
    def __init__(self, json: Dict):
        if not json:
            raise EGRNError(f'Server responce is empty')
        self.errors = json['error']
        if self.errors:
            raise EGRNError(f'`errors` field in server responce is not empty: {self.errors}')