from typing import List, Dict

from egrn_api import (PropertyObject,
                      process_objects,
                      APIObject)

class Search(APIObject):
    def __init__(self, json: Dict):
        super().__init__(json)
        self.objects: List[PropertyObject] = list(process_objects(json['objects']))
        self.found: int = json['found']
        self.region: str = json['region']
        self.error: List[str] = json['error']
