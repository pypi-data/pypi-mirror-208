from cyberpay_utils.company.proto import company_pb2 as _company_pb2
from cyberpay_utils.company.proto import company_user_pb2 as _company_user_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCompanyByIdRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetCompanyUserByIdRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetCompanyUserContractMetaRequest(_message.Message):
    __slots__ = ["company_user_id"]
    COMPANY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    company_user_id: int
    def __init__(self, company_user_id: _Optional[int] = ...) -> None: ...

class GetCompanyUserContractMetaResponse(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class GetCompanyUsersRequest(_message.Message):
    __slots__ = ["company_id", "contract", "is_active", "state", "type", "user_id"]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    company_id: int
    contract: bool
    is_active: bool
    state: str
    type: str
    user_id: int
    def __init__(self, company_id: _Optional[int] = ..., user_id: _Optional[int] = ..., state: _Optional[str] = ..., type: _Optional[str] = ..., contract: bool = ..., is_active: bool = ...) -> None: ...

class GetCompanyUsersResponse(_message.Message):
    __slots__ = ["company_users"]
    COMPANY_USERS_FIELD_NUMBER: _ClassVar[int]
    company_users: _containers.RepeatedCompositeFieldContainer[_company_user_pb2.CompanyUser]
    def __init__(self, company_users: _Optional[_Iterable[_Union[_company_user_pb2.CompanyUser, _Mapping]]] = ...) -> None: ...

class SetCompanyUserIsActiveRequest(_message.Message):
    __slots__ = ["company_user_id", "is_active"]
    COMPANY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    company_user_id: int
    is_active: bool
    def __init__(self, company_user_id: _Optional[int] = ..., is_active: bool = ...) -> None: ...

class SubscibeCompanyRequest(_message.Message):
    __slots__ = ["code", "user_id"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    code: str
    user_id: int
    def __init__(self, code: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...
