from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetDealIsValidRequest(_message.Message):
    __slots__ = ["deal_id"]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    deal_id: str
    def __init__(self, deal_id: _Optional[str] = ...) -> None: ...

class GetDealIsValidResponse(_message.Message):
    __slots__ = ["is_valid", "reasons"]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    REASONS_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    reasons: str
    def __init__(self, is_valid: bool = ..., reasons: _Optional[str] = ...) -> None: ...
