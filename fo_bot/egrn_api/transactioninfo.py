from typing import NamedTuple, List

from egrn_api import APIObject


class PayMethod:
    def __init__(self, raw_method):
        self.name: str = raw_method['name']
        self.allowed: bool = raw_method['allowed']


class Free(PayMethod):
    def __init__(self, raw_method):
        super().__init__(raw_method)
        self.confirm_code: str = raw_method['confirm_code']
        self.confirm_link: str = raw_method['confirm_link']


class PA(Free):
    def __init__(self, raw_method):
        super().__init__(raw_method)
        self.balance: int = raw_method['balance']
        self.sufficient_funds: bool = raw_method['sufficient_funds']


class PayMethodOption(NamedTuple):
    name: str
    img: str
    link: str


class Other(PayMethod):
    def __init__(self, raw_method):
        PayMethod.__init__(raw_method)
        self.methods: List[PayMethodOption]
        for i in raw_method['methods']:
            self.methods.append(PayMethodOption(name=i['name'],
                                                img=i['img'],
                                                link=i['link']
                                                )
                                )


class PayMethods:
    def __init__(self, raw_methods):
        self.free: Free = Free(raw_methods['free'])
        self.pa: PA = PA(raw_methods['PA'])
        self.other: Other = Other(raw_methods['other'])


class TransactionInfo(APIObject):
    def __init__(self, json):
        super().__init__(json)
        self.transaction_id: int = json['transaction_id']
        self.service: str = json['service']
        self.caption: str = json['caption']
        self.description: str = json['description']
        self.cost: int = json['cost']
        self.paid: bool = json['paid']
        self.paid_from: str = json['paid_from']
        self.date_create: str = json['date_create']
        self.date_paid: str = json['date_paid']
        self.pay_method: PayMethods = PayMethods(json[''])
        self.error: List[str] = json['error']