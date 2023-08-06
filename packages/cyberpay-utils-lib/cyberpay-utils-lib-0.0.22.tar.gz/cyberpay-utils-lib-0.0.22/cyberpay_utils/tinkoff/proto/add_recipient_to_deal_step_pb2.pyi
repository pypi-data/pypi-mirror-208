from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddRecipientToDealStepRequest(_message.Message):
    __slots__ = ["amount", "bank_details_id", "beneficiary_id", "deal_id", "keep_on_virtual_account", "purpose", "step_id", "tax"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BANK_DETAILS_ID_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    KEEP_ON_VIRTUAL_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_FIELD_NUMBER: _ClassVar[int]
    amount: float
    bank_details_id: str
    beneficiary_id: str
    deal_id: str
    keep_on_virtual_account: bool
    purpose: str
    step_id: str
    tax: float
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., amount: _Optional[float] = ..., tax: _Optional[float] = ..., purpose: _Optional[str] = ..., bank_details_id: _Optional[str] = ..., keep_on_virtual_account: bool = ...) -> None: ...

class AddRecipientToDealStepResponse(_message.Message):
    __slots__ = ["amount", "bank_details_id", "beneficiary_id", "deal_id", "keep_on_virtual_account", "purpose", "recipient_id", "step_id", "tax"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BANK_DETAILS_ID_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    KEEP_ON_VIRTUAL_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_FIELD_NUMBER: _ClassVar[int]
    amount: float
    bank_details_id: str
    beneficiary_id: str
    deal_id: str
    keep_on_virtual_account: bool
    purpose: str
    recipient_id: str
    step_id: str
    tax: float
    def __init__(self, deal_id: _Optional[str] = ..., step_id: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., recipient_id: _Optional[str] = ..., amount: _Optional[float] = ..., tax: _Optional[float] = ..., purpose: _Optional[str] = ..., bank_details_id: _Optional[str] = ..., keep_on_virtual_account: bool = ...) -> None: ...
