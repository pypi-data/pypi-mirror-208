from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Receipt(_message.Message):
    __slots__ = ["active_workers", "company_id", "from_period", "to_period", "uuid"]
    ACTIVE_WORKERS_FIELD_NUMBER: _ClassVar[int]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_PERIOD_FIELD_NUMBER: _ClassVar[int]
    TO_PERIOD_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    active_workers: int
    company_id: int
    from_period: str
    to_period: str
    uuid: str
    def __init__(self, uuid: _Optional[str] = ..., company_id: _Optional[int] = ..., from_period: _Optional[str] = ..., to_period: _Optional[str] = ..., active_workers: _Optional[int] = ...) -> None: ...
