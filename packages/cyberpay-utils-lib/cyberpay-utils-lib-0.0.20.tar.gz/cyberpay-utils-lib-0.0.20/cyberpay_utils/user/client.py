import grpc

from .proto import user_pb2, user_service_pb2, user_service_pb2_grpc


class UserServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def auth_user(
        self, request: user_service_pb2.AuthUserRequest
    ) -> user_service_pb2.AuthUserResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.AuthUser(request)
            return response

    def get_user_by_id(
        self, request: user_service_pb2.GetUserByIdRequest
    ) -> user_service_pb2.GetUserByIdResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.GetUserById(request)
            return response

    def create_manager(
        self, request: user_service_pb2.CreateManagerRequest
    ) -> user_pb2.User:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.CreateManager(request)
            return response

    def get_company_users_json(
        self, request: user_service_pb2.GetCompanyUsersJsonRequest
    ) -> user_service_pb2.GetCompanyUsersJsonResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.GetCompanyUsersJson(request)
            return response

    def edit_user_by_id(
        self, request: user_service_pb2.EditUserByIdRequest
    ) -> user_pb2.User:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.EditUserById(request)
            return response

    def get_user_data_for_contract_json(
        self, request: user_service_pb2.GetUserDataForContractJsonRequest
    ) -> user_service_pb2.GetUserDataForContractJsonResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.GetUserDataForContractJson(request)
            return response
