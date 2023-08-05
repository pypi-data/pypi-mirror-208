from cyberpay_utils.tinkoff.proto import bank_statement_operation_pb2 as _bank_statement_operation_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBankStatementRequest(_message.Message):
    __slots__ = ["account_number", "from_date", "till_date"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TILL_DATE_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    from_date: str
    till_date: str
    def __init__(self, account_number: _Optional[str] = ..., from_date: _Optional[str] = ..., till_date: _Optional[str] = ...) -> None: ...

class GetBankStatementResponse(_message.Message):
    __slots__ = ["account_number", "income", "operation", "outcome", "saldo_in", "saldo_out"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INCOME_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    SALDO_IN_FIELD_NUMBER: _ClassVar[int]
    SALDO_OUT_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    income: float
    operation: _containers.RepeatedCompositeFieldContainer[_bank_statement_operation_pb2.BankStatementOperation]
    outcome: float
    saldo_in: float
    saldo_out: float
    def __init__(self, account_number: _Optional[str] = ..., saldo_in: _Optional[float] = ..., income: _Optional[float] = ..., outcome: _Optional[float] = ..., saldo_out: _Optional[float] = ..., operation: _Optional[_Iterable[_Union[_bank_statement_operation_pb2.BankStatementOperation, _Mapping]]] = ...) -> None: ...
