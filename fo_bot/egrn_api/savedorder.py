from typing import Dict, NamedTuple, Optional, List

from fo_bot.egrn_api import APIObject

class DocumentsId(NamedTuple):
    xzp: Optional[int]
    sopp: Optional[int]

class SavedOrder(APIObject):
    def __init__(self, json: Dict):
        super().__init__(json)
        self.transaction_id: int = json['transaction_id']
        raw_ids = json['documents_id']
        self.documents_id: DocumentsId = DocumentsId(xzp=raw_ids.get('XZP', None),
                                                     sopp=raw_ids.get('SOPP', None)
                                                     )
        self.paid: bool = json['paid']
        self.error: List[str] = json['error']