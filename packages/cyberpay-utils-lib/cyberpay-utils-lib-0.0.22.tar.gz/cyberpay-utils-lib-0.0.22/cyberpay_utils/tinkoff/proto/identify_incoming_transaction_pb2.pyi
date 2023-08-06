from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AmountDistributionItem(_message.Message):
    __slots__ = ["amount", "beneficiary_id"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    amount: float
    beneficiary_id: str
    def __init__(self, beneficiary_id: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class IdentifyIncomingTransactionRequest(_message.Message):
    __slots__ = ["amount_distribution", "operation_id"]
    AMOUNT_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    amount_distribution: _containers.RepeatedCompositeFieldContainer[AmountDistributionItem]
    operation_id: str
    def __init__(self, operation_id: _Optional[str] = ..., amount_distribution: _Optional[_Iterable[_Union[AmountDistributionItem, _Mapping]]] = ...) -> None: ...
