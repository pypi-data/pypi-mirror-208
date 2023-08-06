from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Profile(_message.Message):
    __slots__ = ["bank_details_id", "beneficiary_id", "citizenship", "dob", "inn", "issued", "issued_code", "ogrnip", "passport", "place_of_issue", "pob", "registration_date", "residence", "snils", "type", "user_id"]
    BANK_DETAILS_ID_FIELD_NUMBER: _ClassVar[int]
    BENEFICIARY_ID_FIELD_NUMBER: _ClassVar[int]
    CITIZENSHIP_FIELD_NUMBER: _ClassVar[int]
    DOB_FIELD_NUMBER: _ClassVar[int]
    INN_FIELD_NUMBER: _ClassVar[int]
    ISSUED_CODE_FIELD_NUMBER: _ClassVar[int]
    ISSUED_FIELD_NUMBER: _ClassVar[int]
    OGRNIP_FIELD_NUMBER: _ClassVar[int]
    PASSPORT_FIELD_NUMBER: _ClassVar[int]
    PLACE_OF_ISSUE_FIELD_NUMBER: _ClassVar[int]
    POB_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    RESIDENCE_FIELD_NUMBER: _ClassVar[int]
    SNILS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    bank_details_id: str
    beneficiary_id: str
    citizenship: str
    dob: str
    inn: str
    issued: str
    issued_code: str
    ogrnip: str
    passport: str
    place_of_issue: str
    pob: str
    registration_date: str
    residence: str
    snils: str
    type: str
    user_id: int
    def __init__(self, user_id: _Optional[int] = ..., citizenship: _Optional[str] = ..., type: _Optional[str] = ..., passport: _Optional[str] = ..., issued: _Optional[str] = ..., issued_code: _Optional[str] = ..., place_of_issue: _Optional[str] = ..., inn: _Optional[str] = ..., snils: _Optional[str] = ..., dob: _Optional[str] = ..., pob: _Optional[str] = ..., residence: _Optional[str] = ..., ogrnip: _Optional[str] = ..., registration_date: _Optional[str] = ..., beneficiary_id: _Optional[str] = ..., bank_details_id: _Optional[str] = ...) -> None: ...
