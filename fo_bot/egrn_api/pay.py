from typing import List

from fo_bot.egrn_api import APIObject


class Pay(APIObject):
    def __init__(self, json):
        super().__init__(json)
        self.paid: bool = json['paid']
        self.cost: int = json['cost']