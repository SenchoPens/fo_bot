from typing import Dict, List, NamedTuple

from egrn_api import APIObject


class OrderedDocument(NamedTuple):
    id: int
    type: str
    state: int
    date_complete: str
    price: int


class OrderInfo(APIObject):
    """Represents server's responce for Cadaster/Orders."""

    def __init__(self, json):
        super().__init__(json)
        self.id: int = json['id']
        self.cadnomer: str = json['cadnomer']
        self.details: Dict = json['details']
        self.comment: str = json['comment']
        self.date_create: str = json['date_create']
        self.price: int = json['price']
        self.documents: List[OrderedDocument] = []
        for raw_document in json['documents']:
            self.documents.append(OrderedDocument(id=raw_document['id'],
                                                  type=raw_document['type'],
                                                  state=raw_document['status'],
                                                  date_complete=raw_document['date_complete'],
                                                  price=raw_document['price'],
                                                  ))
