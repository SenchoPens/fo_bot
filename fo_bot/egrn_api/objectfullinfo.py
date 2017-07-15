from typing import NamedTuple, List, Dict

from egrn_api import (
    Documents,
    PropertyObject,
    process_object,
    APIObject
)


class EGRN(NamedTuple):
    property_object: PropertyObject
    details: Dict[str, str]


class ObjectFullInfo(APIObject):
    def __init__(self, json: Dict):
        super().__init__(json)
        self.egrn: EGRN = ObjectFullInfo.process_egrn(json['EGRN'])
        self.region: str = json['region']
        self.documents: Documents = Documents(json['documents'])
        self.encoded_object: str = json['encoded_object']

    @staticmethod
    def process_egrn(raw_egrn: Dict) -> EGRN:
        return EGRN(property_object=process_object(raw_egrn['object']),
                    details=raw_egrn['details']
                    )