from cyberpay_utils.user.proto import user_pb2 as _user_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthUserRequest(_message.Message):
    __slots__ = ["login", "password"]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    login: str
    password: str
    def __init__(self, login: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class AuthUserResponse(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ...) -> None: ...

class CreateManagerRequest(_message.Message):
    __slots__ = ["email", "name", "patronymic", "phone", "surname"]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATRONYMIC_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    SURNAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    patronymic: str
    phone: str
    surname: str
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ..., surname: _Optional[str] = ..., patronymic: _Optional[str] = ..., phone: _Optional[str] = ...) -> None: ...

class EditUserByIdRequest(_message.Message):
    __slots__ = ["data", "id"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    data: EditUserByIdRequestData
    id: int
    def __init__(self, id: _Optional[int] = ..., data: _Optional[_Union[EditUserByIdRequestData, _Mapping]] = ...) -> None: ...

class EditUserByIdRequestData(_message.Message):
    __slots__ = ["email", "login", "name", "patronymic", "phone", "surname"]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATRONYMIC_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    SURNAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    login: str
    name: str
    patronymic: str
    phone: str
    surname: str
    def __init__(self, email: _Optional[str] = ..., login: _Optional[str] = ..., name: _Optional[str] = ..., surname: _Optional[str] = ..., patronymic: _Optional[str] = ..., phone: _Optional[str] = ...) -> None: ...

class GetCompanyUsersJsonRequest(_message.Message):
    __slots__ = ["filter_params", "type"]
    FILTER_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    filter_params: str
    type: str
    def __init__(self, type: _Optional[str] = ..., filter_params: _Optional[str] = ...) -> None: ...

class GetCompanyUsersJsonResponse(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class GetUserByIdRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetUserByIdResponse(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ...) -> None: ...

class GetUserDataForContractJsonRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetUserDataForContractJsonResponse(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...
