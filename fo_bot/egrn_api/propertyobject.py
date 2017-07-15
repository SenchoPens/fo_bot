from typing import (
    NamedTuple,
    Generator,
    List,
    Dict
)


class PropertyObject(NamedTuple):
    cadnomer: str
    address: str
    property_type: str
    area: str
    category: str


def process_objects(raw_objects: List[Dict]) -> Generator[PropertyObject, None, None]:
    for raw_object in raw_objects:
        yield process_object(raw_object)


def process_object(raw_object: Dict) -> PropertyObject:
    return PropertyObject(cadnomer=raw_object['CADNOMER'],
                          address=raw_object['ADDRESS'],
                          property_type=raw_object['TYPE'],
                          area=raw_object['AREA'],
                          category=raw_object['CATEGORY'])