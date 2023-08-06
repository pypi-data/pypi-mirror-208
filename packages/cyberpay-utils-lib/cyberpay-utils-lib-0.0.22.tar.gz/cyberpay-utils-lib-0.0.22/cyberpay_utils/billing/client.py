import grpc
from google import protobuf as google_proto

from .proto import billing_pb2, billing_pb2_grpc


class BillingServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def create_receipt(
        self, request: billing_pb2.CreateReceiptRequest
    ) -> billing_pb2.CreateReceiptRequest:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = billing_pb2_grpc.BillingStub(channel)
            response = stub.CreateReceipt(request)
            return response

    def get_all_receipts(self) -> billing_pb2.GetAllReceiptsResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = billing_pb2_grpc.BillingStub(channel)
            response = stub.GetAllReceipts(google_proto.empty_pb2.Empty())
            return response

    def get_current_receipt(
        self, request: billing_pb2.GetCurrentReceiptRequest
    ) -> billing_pb2.GetCurrentReceiptResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = billing_pb2_grpc.BillingStub(channel)
            response = stub.GetCurrentReceipt(request)
            return response

    def increase_active_workers(
        self, request: billing_pb2.IncreaseActiveWorkersRequest
    ) -> billing_pb2.IncreaseActiveWorkersResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = billing_pb2_grpc.BillingStub(channel)
            response = stub.IncreaseActiveWorkers(request)
            return response
