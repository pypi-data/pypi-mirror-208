from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CompanyUser(_message.Message):
    __slots__ = ["about", "company_id", "contract", "id", "is_active", "state", "type", "user_id"]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    about: str
    company_id: int
    contract: bool
    id: int
    is_active: bool
    state: str
    type: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., company_id: _Optional[int] = ..., user_id: _Optional[int] = ..., state: _Optional[str] = ..., type: _Optional[str] = ..., about: _Optional[str] = ..., contract: bool = ..., is_active: bool = ...) -> None: ...
