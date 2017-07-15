from typing import NamedTuple, Dict

from egrn_api import APIObject


class Document(NamedTuple):
    label: str
    available: bool
    price: int


class Documents:
    def __init__(self, json: Dict):
        self.xzp: Document = Documents.process_document(json['XZP'])
        self.sopp: Document = Documents.process_document(json['SOPP'])

    @staticmethod
    def process_document(raw_document: Dict):
        return Document(label=raw_document['label'],
                        available=raw_document['available'],
                        price=raw_document['price']
                        )