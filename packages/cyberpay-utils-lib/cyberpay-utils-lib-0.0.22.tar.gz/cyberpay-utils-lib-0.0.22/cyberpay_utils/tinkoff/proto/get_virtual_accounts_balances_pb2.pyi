from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BalanceListItem(_message.Message):
    __slots__ = ["account_number", "amount", "amount_on_hold", "beneficiary_id"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_ON_HOLD_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    amount: float
    amount_on_hold: float
    beneficiary_id: str
    def __init__(self, beneficiary_id: _Optional[str] = ..., account_number: _Optional[str] = ..., amount: _Optional[float] = ..., amount_on_hold: _Optional[float] = ...) -> None: ...

class GetVirtualAccountsBalancesRequest(_message.Message):
    __slots__ = ["account_number", "beneficiary_id", "limit", "offset"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    beneficiary_id: str
    limit: int
    offset: int
    def __init__(self, account_number: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetVirtualAccountsBalancesResponse(_message.Message):
    __slots__ = ["limit", "offset", "results", "size", "total"]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    results: _containers.RepeatedCompositeFieldContainer[BalanceListItem]
    size: int
    total: int
    def __init__(self, offset: _Optional[int] = ..., limit: _Optional[int] = ..., size: _Optional[int] = ..., total: _Optional[int] = ..., results: _Optional[_Iterable[_Union[BalanceListItem, _Mapping]]] = ...) -> None: ...
