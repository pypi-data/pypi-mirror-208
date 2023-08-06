from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SendCloseDocumentEmailRequest(_message.Message):
    __slots__ = ["company", "emails", "files", "user"]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    company: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    files: _containers.RepeatedScalarFieldContainer[str]
    user: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., files: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., company: _Optional[str] = ...) -> None: ...

class SendContractEmailRequest(_message.Message):
    __slots__ = ["company", "emails", "files", "user"]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    company: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    files: _containers.RepeatedScalarFieldContainer[str]
    user: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., files: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., company: _Optional[str] = ...) -> None: ...

class SendLoginPasswordEmailRequest(_message.Message):
    __slots__ = ["emails", "login", "password"]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    emails: _containers.RepeatedScalarFieldContainer[str]
    login: str
    password: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., login: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class SendNewEmployeeEmailRequest(_message.Message):
    __slots__ = ["company", "emails", "url"]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    company: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    url: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., url: _Optional[str] = ..., company: _Optional[str] = ...) -> None: ...

class SendNewSupportRequestEmailRequest(_message.Message):
    __slots__ = ["contact_email", "contact_phone", "emails", "files", "message", "user"]
    CONTACT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    CONTACT_PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    contact_email: str
    contact_phone: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    files: _containers.RepeatedScalarFieldContainer[str]
    message: str
    user: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., files: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., contact_email: _Optional[str] = ..., contact_phone: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class SendNewTaskEmailRequest(_message.Message):
    __slots__ = ["company", "emails", "files", "user"]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    company: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    files: _containers.RepeatedScalarFieldContainer[str]
    user: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., files: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., company: _Optional[str] = ...) -> None: ...

class SendOtpCodeEmailRequest(_message.Message):
    __slots__ = ["code", "emails", "user"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    code: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    user: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class SendResetPasswordEmailRequest(_message.Message):
    __slots__ = ["emails", "link", "login"]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    emails: _containers.RepeatedScalarFieldContainer[str]
    link: str
    login: str
    def __init__(self, emails: _Optional[_Iterable[str]] = ..., login: _Optional[str] = ..., link: _Optional[str] = ...) -> None: ...
