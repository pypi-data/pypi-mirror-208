from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddDeponentToDealStepRequest(_message.Message):
    __slots__ = ["amount", "beneficiary_id", "deal_id", "step_id"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    amount: float
    beneficiary_id: str
    deal_id: str
    step_id: str
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class AddDeponentToDealStepResponse(_message.Message):
    __slots__ = ["amount", "beneficiary_id", "deal_id", "step_id"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    amount: float
    beneficiary_id: str
    deal_id: str
    step_id: str
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...
