from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BankStatementOperation(_message.Message):
    __slots__ = ["amount", "charge_date", "creator_status", "date", "draw_date", "execution_order", "id", "kbk", "oktmo", "operation_id", "operation_type", "payer_account", "payer_bank", "payer_bic", "payer_corr_account", "payer_inn", "payer_kpp", "payer_name", "payment_purpose", "payment_type", "recipient", "recipient_account", "recipient_bank", "recipient_bic", "recipient_corr_account", "recipient_inn", "recipient_kpp", "tax_doc_date", "tax_doc_number", "tax_evidence", "tax_period", "tax_type", "uin"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CHARGE_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATOR_STATUS_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DRAW_DATE_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ORDER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    KBK_FIELD_NUMBER: _ClassVar[int]
    OKTMO_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYER_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PAYER_BANK_FIELD_NUMBER: _ClassVar[int]
    PAYER_BIC_FIELD_NUMBER: _ClassVar[int]
    PAYER_CORR_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PAYER_INN_FIELD_NUMBER: _ClassVar[int]
    PAYER_KPP_FIELD_NUMBER: _ClassVar[int]
    PAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_PURPOSE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_BANK_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_BIC_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_CORR_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_INN_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_KPP_FIELD_NUMBER: _ClassVar[int]
    TAX_DOC_DATE_FIELD_NUMBER: _ClassVar[int]
    TAX_DOC_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TAX_EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    TAX_PERIOD_FIELD_NUMBER: _ClassVar[int]
    TAX_TYPE_FIELD_NUMBER: _ClassVar[int]
    UIN_FIELD_NUMBER: _ClassVar[int]
    amount: float
    charge_date: str
    creator_status: str
    date: str
    draw_date: str
    execution_order: str
    id: str
    kbk: str
    oktmo: str
    operation_id: str
    operation_type: str
    payer_account: str
    payer_bank: str
    payer_bic: str
    payer_corr_account: str
    payer_inn: str
    payer_kpp: str
    payer_name: str
    payment_purpose: str
    payment_type: str
    recipient: str
    recipient_account: str
    recipient_bank: str
    recipient_bic: str
    recipient_corr_account: str
    recipient_inn: str
    recipient_kpp: str
    tax_doc_date: str
    tax_doc_number: str
    tax_evidence: str
    tax_period: str
    tax_type: str
    uin: str
    def __init__(self, operation_id: _Optional[str] = ..., id: _Optional[str] = ..., date: _Optional[str] = ..., amount: _Optional[float] = ..., draw_date: _Optional[str] = ..., payer_name: _Optional[str] = ..., payer_inn: _Optional[str] = ..., payer_account: _Optional[str] = ..., payer_corr_account: _Optional[str] = ..., payer_bic: _Optional[str] = ..., payer_bank: _Optional[str] = ..., charge_date: _Optional[str] = ..., recipient: _Optional[str] = ..., recipient_inn: _Optional[str] = ..., recipient_account: _Optional[str] = ..., recipient_corr_account: _Optional[str] = ..., recipient_bic: _Optional[str] = ..., recipient_bank: _Optional[str] = ..., payment_type: _Optional[str] = ..., operation_type: _Optional[str] = ..., uin: _Optional[str] = ..., payment_purpose: _Optional[str] = ..., creator_status: _Optional[str] = ..., payer_kpp: _Optional[str] = ..., recipient_kpp: _Optional[str] = ..., kbk: _Optional[str] = ..., oktmo: _Optional[str] = ..., tax_evidence: _Optional[str] = ..., tax_period: _Optional[str] = ..., tax_doc_number: _Optional[str] = ..., tax_doc_date: _Optional[str] = ..., tax_type: _Optional[str] = ..., execution_order: _Optional[str] = ...) -> None: ...
