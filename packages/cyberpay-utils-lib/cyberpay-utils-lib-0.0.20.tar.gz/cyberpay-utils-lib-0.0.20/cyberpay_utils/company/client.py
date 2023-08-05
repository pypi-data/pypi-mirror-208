import grpc
from google.protobuf import empty_pb2

from .proto import company_service_pb2, company_service_pb2_grpc


class CompanyServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def subscibe_company(
        self, request: company_service_pb2.SubscibeCompanyRequest
    ) -> empty_pb2.Empty:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.SubscibeCompany(request)
            return response
