from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AcceptDealRequest(_message.Message):
    __slots__ = ["deal_id"]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    deal_id: str
    def __init__(self, deal_id: _Optional[str] = ...) -> None: ...
