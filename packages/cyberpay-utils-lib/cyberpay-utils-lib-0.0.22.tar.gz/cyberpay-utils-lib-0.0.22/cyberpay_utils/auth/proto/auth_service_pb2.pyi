from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class IsUserAuthenticatedRequest(_message.Message):
    __slots__ = ["access"]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    access: str
    def __init__(self, access: _Optional[str] = ...) -> None: ...

class IsUserAuthenticatedResponse(_message.Message):
    __slots__ = ["user_id"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...
