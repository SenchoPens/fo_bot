from typing import List
from functools import partial

import requests

from settings import API_TOKEN
from egrn_api import (
    Search,
    ObjectFullInfo,
    SavedOrder,
    TransactionInfo,
    Pay
)


API_URL: str = 'https://apirosreestr.ru/api/'


class API:
    _cadaster_url = API_URL + 'cadaster/'
    _search_url = _cadaster_url + 'search'
    _object_full_info_url = _cadaster_url + 'objectInfoFull'
    _save_order_url = _cadaster_url + 'save_order'
    _orders = _cadaster_url + 'orders'
    _download = _cadaster_url + 'download'

    _transaction_url = API_URL + 'transaction/'
    _transaction_info_url = _transaction_url + 'info'
    _pay_url = _transaction_url + 'pay'

    def __init__(self, token: str):
        self.token = token
        self.headers = {'Token': token}

        self.get = partial(requests.get, headers=self.headers)
        self.post = partial(requests.post, headers=self.headers)

    def search(self, query: str) -> Search:
        return Search(json=self.post(url=API._search_url,
                                     data={'query': query}
                                     ).json()
                      )

    def get_object_full_info(self, cadnomer) -> ObjectFullInfo:
        return ObjectFullInfo(json=self.post(url=API._object_full_info_url,
                                             data={'query': cadnomer}
                                             ).json()
                              )

    def save_order(self, object_code: str, *, documents: List[str]) -> SavedOrder:
        if not documents:
            raise ValueError
        print(documents)

        return SavedOrder(json=self.post(url=API._save_order_url,
                                         data={'encoded_object': object_code,
                                               'documents[]': documents,
                                               }
                                         ).json()
                          )

    def get_transaction_info(self, transaction_id: int) -> TransactionInfo:
        return TransactionInfo(json=self.post(url=API._transaction_info_url,
                                              data={'id': transaction_id}
                                              ).json()
                               )

    def pay(self, transaction_id: int, confirm_code: int) -> Pay:
        return Pay(json=self.post(url=API._pay_url,
                                  data={'id': transaction_id,
                                        'confirm': confirm_code
                                        }
                                  ).json()
                   )


if __name__ == '__main__':
    api = API(API_TOKEN)
    ex_cad = '76:23:060701:3277'
    res = api.search(ex_cad)
    print('Example cadnomer found property', res.objects[0])
    info = api.get_object_full_info(res.objects[0].cadnomer)
    print(info.encoded_object)
    print(info.egrn.property_object.address)
    print(info.encoded_object)
    order = api.save_order(info.encoded_object, documents='XZP')

    #print(api.get_transaction_info(ex_id))
