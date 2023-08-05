from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetDealStepByIDRequest(_message.Message):
    __slots__ = ["deal_id", "step_id"]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    deal_id: str
    step_id: str
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ...) -> None: ...

class GetDealStepByIDResponse(_message.Message):
    __slots__ = ["deal_id", "description", "status", "step_id", "step_number"]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_NUMBER_FIELD_NUMBER: _ClassVar[int]
    deal_id: str
    description: str
    status: str
    step_id: str
    step_number: int
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ..., step_number: _Optional[int] = ..., description: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...
