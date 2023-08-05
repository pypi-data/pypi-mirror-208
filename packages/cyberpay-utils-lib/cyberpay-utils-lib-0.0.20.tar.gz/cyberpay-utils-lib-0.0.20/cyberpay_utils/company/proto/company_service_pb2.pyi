from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SubscibeCompanyRequest(_message.Message):
    __slots__ = ["code", "user_id"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    code: str
    user_id: int
    def __init__(self, code: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...
