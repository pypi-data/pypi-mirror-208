from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ["avatar", "created_at", "email", "id", "is_active", "is_banned", "is_manager", "is_staff", "is_verified", "login", "name", "open_code", "otp_code", "patronymic", "phone", "status", "surname"]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_BANNED_FIELD_NUMBER: _ClassVar[int]
    IS_MANAGER_FIELD_NUMBER: _ClassVar[int]
    IS_STAFF_FIELD_NUMBER: _ClassVar[int]
    IS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPEN_CODE_FIELD_NUMBER: _ClassVar[int]
    OTP_CODE_FIELD_NUMBER: _ClassVar[int]
    PATRONYMIC_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SURNAME_FIELD_NUMBER: _ClassVar[int]
    avatar: str
    created_at: str
    email: str
    id: int
    is_active: bool
    is_banned: bool
    is_manager: bool
    is_staff: bool
    is_verified: bool
    login: str
    name: str
    open_code: str
    otp_code: str
    patronymic: str
    phone: str
    status: str
    surname: str
    def __init__(self, id: _Optional[int] = ..., email: _Optional[str] = ..., login: _Optional[str] = ..., avatar: _Optional[str] = ..., name: _Optional[str] = ..., surname: _Optional[str] = ..., patronymic: _Optional[str] = ..., phone: _Optional[str] = ..., is_manager: bool = ..., is_staff: bool = ..., is_active: bool = ..., is_verified: bool = ..., is_banned: bool = ..., status: _Optional[str] = ..., open_code: _Optional[str] = ..., otp_code: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...
