import grpc
from google.protobuf import empty_pb2

from .proto import (
    company_pb2,
    company_service_pb2,
    company_service_pb2_grpc,
    company_user_pb2,
)


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

    def get_company_users(
        self, request: company_service_pb2.GetCompanyUsersRequest
    ) -> company_service_pb2.GetCompanyUsersResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.GetCompanyUsers(request)
            return response

    def get_company_by_id(
        self, request: company_service_pb2.GetCompanyByIdRequest
    ) -> company_pb2.Company:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.GetCompanyById(request)
            return response

    def get_company_user_by_id(
        self, request: company_service_pb2.GetCompanyUserByIdRequest
    ) -> company_user_pb2.CompanyUser:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.GetCompanyUserById(request)
            return response

    def get_company_user_contract_meta(
        self, request: company_service_pb2.GetCompanyUserContractMetaRequest
    ) -> company_service_pb2.GetCompanyUserContractMetaResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.GetCompanyUserContractMeta(request)
            return response

    def set_company_user_is_active(
        self, request: company_service_pb2.SetCompanyUserIsActiveRequest
    ) -> empty_pb2.Empty:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = company_service_pb2_grpc.CompanyServiceStub(channel)
            response = stub.SetCompanyUserIsActive(request)
            return response
