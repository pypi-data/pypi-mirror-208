from google.protobuf import empty_pb2 as _empty_pb2
from cyberpay_utils.billing.proto import receipt_pb2 as _receipt_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateReceiptRequest(_message.Message):
    __slots__ = ["company_id"]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    company_id: int
    def __init__(self, company_id: _Optional[int] = ...) -> None: ...

class CreateReceiptResponse(_message.Message):
    __slots__ = ["receipt"]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    receipt: _receipt_pb2.Receipt
    def __init__(self, receipt: _Optional[_Union[_receipt_pb2.Receipt, _Mapping]] = ...) -> None: ...

class GetAllReceiptsResponse(_message.Message):
    __slots__ = ["receipts"]
    RECEIPTS_FIELD_NUMBER: _ClassVar[int]
    receipts: _containers.RepeatedCompositeFieldContainer[_receipt_pb2.Receipt]
    def __init__(self, receipts: _Optional[_Iterable[_Union[_receipt_pb2.Receipt, _Mapping]]] = ...) -> None: ...

class GetCurrentReceiptRequest(_message.Message):
    __slots__ = ["company_id"]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    company_id: int
    def __init__(self, company_id: _Optional[int] = ...) -> None: ...

class GetCurrentReceiptResponse(_message.Message):
    __slots__ = ["receipt"]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    receipt: _receipt_pb2.Receipt
    def __init__(self, receipt: _Optional[_Union[_receipt_pb2.Receipt, _Mapping]] = ...) -> None: ...

class IncreaseActiveWorkersRequest(_message.Message):
    __slots__ = ["company_id"]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    company_id: int
    def __init__(self, company_id: _Optional[int] = ...) -> None: ...

class IncreaseActiveWorkersResponse(_message.Message):
    __slots__ = ["receipt"]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    receipt: _receipt_pb2.Receipt
    def __init__(self, receipt: _Optional[_Union[_receipt_pb2.Receipt, _Mapping]] = ...) -> None: ...
