from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateDealRequest(_message.Message):
    __slots__ = ["account_number"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    def __init__(self, account_number: _Optional[str] = ...) -> None: ...

class CreateDealResponse(_message.Message):
    __slots__ = ["account_number", "deal_id", "status"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    deal_id: str
    status: str
    def __init__(self, deal_id: _Optional[str] = ..., account_number: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...
