from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Company(_message.Message):
    __slots__ = ["address", "bankDetails_id", "bank_info", "beneficiary_id", "bik", "code", "company_type", "created_at", "email", "full_name", "inn", "kpp", "ks", "ogrn", "okpo", "owner", "phone", "receipt_data", "rs", "short_name", "total_price"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BANKDETAILS_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_INFO_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    BIK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    COMPANY_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    INN_FIELD_NUMBER: _ClassVar[int]
    KPP_FIELD_NUMBER: _ClassVar[int]
    KS_FIELD_NUMBER: _ClassVar[int]
    OGRN_FIELD_NUMBER: _ClassVar[int]
    OKPO_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    RECEIPT_DATA_FIELD_NUMBER: _ClassVar[int]
    RS_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    address: str
    bankDetails_id: str
    bank_info: str
    beneficiary_id: str
    bik: str
    code: str
    company_type: str
    created_at: str
    email: str
    full_name: str
    inn: str
    kpp: str
    ks: str
    ogrn: str
    okpo: str
    owner: str
    phone: str
    receipt_data: str
    rs: str
    short_name: str
    total_price: str
    def __init__(self, full_name: _Optional[str] = ..., short_name: _Optional[str] = ..., email: _Optional[str] = ..., address: _Optional[str] = ..., company_type: _Optional[str] = ..., owner: _Optional[str] = ..., code: _Optional[str] = ..., phone: _Optional[str] = ..., inn: _Optional[str] = ..., kpp: _Optional[str] = ..., ogrn: _Optional[str] = ..., okpo: _Optional[str] = ..., rs: _Optional[str] = ..., ks: _Optional[str] = ..., bik: _Optional[str] = ..., bank_info: _Optional[str] = ..., created_at: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., bankDetails_id: _Optional[str] = ..., total_price: _Optional[str] = ..., receipt_data: _Optional[str] = ...) -> None: ...
