from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetIncomingTransactionsRequest(_message.Message):
    __slots__ = ["account_number", "limit", "offset"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    limit: int
    offset: int
    def __init__(self, account_number: _Optional[str] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetIncomingTransactionsResponse(_message.Message):
    __slots__ = ["limit", "offset", "results", "size", "total"]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    results: _containers.RepeatedCompositeFieldContainer[IncomingTransactionListItem]
    size: int
    total: int
    def __init__(self, offset: _Optional[int] = ..., limit: _Optional[int] = ..., size: _Optional[int] = ..., total: _Optional[int] = ..., results: _Optional[_Iterable[_Union[IncomingTransactionListItem, _Mapping]]] = ...) -> None: ...

class IncomingTransactionListItem(_message.Message):
    __slots__ = ["account_number", "amount", "authorization_date", "charge_date", "currency", "document_number", "draw_date", "operation_amount", "operation_currency", "operation_id", "payer_account_number", "payer_bank_name", "payer_bank_swift_code", "payer_bik", "payer_corr_account_number", "payer_inn", "payer_kpp", "payer_name", "payment_purpose", "transaction_date"]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_DATE_FIELD_NUMBER: _ClassVar[int]
    CHARGE_DATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DRAW_DATE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    OPERATION_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    PAYER_ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PAYER_BANK_NAME_FIELD_NUMBER: _ClassVar[int]
    PAYER_BANK_SWIFT_CODE_FIELD_NUMBER: _ClassVar[int]
    PAYER_BIK_FIELD_NUMBER: _ClassVar[int]
    PAYER_CORR_ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PAYER_INN_FIELD_NUMBER: _ClassVar[int]
    PAYER_KPP_FIELD_NUMBER: _ClassVar[int]
    PAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_PURPOSE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_DATE_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    amount: float
    authorization_date: str
    charge_date: str
    currency: str
    document_number: str
    draw_date: str
    operation_amount: float
    operation_currency: str
    operation_id: str
    payer_account_number: str
    payer_bank_name: str
    payer_bank_swift_code: str
    payer_bik: str
    payer_corr_account_number: str
    payer_inn: str
    payer_kpp: str
    payer_name: str
    payment_purpose: str
    transaction_date: str
    def __init__(self, account_number: _Optional[str] = ..., operation_id: _Optional[str] = ..., amount: _Optional[float] = ..., currency: _Optional[str] = ..., operation_amount: _Optional[float] = ..., operation_currency: _Optional[str] = ..., payer_bik: _Optional[str] = ..., payer_kpp: _Optional[str] = ..., payer_inn: _Optional[str] = ..., payer_bank_name: _Optional[str] = ..., payer_bank_swift_code: _Optional[str] = ..., payer_account_number: _Optional[str] = ..., payer_corr_account_number: _Optional[str] = ..., payer_name: _Optional[str] = ..., payment_purpose: _Optional[str] = ..., document_number: _Optional[str] = ..., charge_date: _Optional[str] = ..., authorization_date: _Optional[str] = ..., transaction_date: _Optional[str] = ..., draw_date: _Optional[str] = ...) -> None: ...
