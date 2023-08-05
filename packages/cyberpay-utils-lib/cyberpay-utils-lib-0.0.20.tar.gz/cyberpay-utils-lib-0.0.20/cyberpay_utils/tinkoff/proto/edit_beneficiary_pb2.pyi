from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EditBeneficiaryRequest(_message.Message):
    __slots__ = ["beneficiary_id", "data"]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    beneficiary_id: str
    data: str
    def __init__(self, beneficiary_id: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...
