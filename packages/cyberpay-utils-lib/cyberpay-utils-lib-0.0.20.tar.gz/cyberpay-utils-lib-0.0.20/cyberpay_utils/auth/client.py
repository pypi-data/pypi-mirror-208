import grpc

from .proto import auth_service_pb2, auth_service_pb2_grpc


class AuthServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def is_user_authenticated(
        self,
        request: auth_service_pb2.IsUserAuthenticatedRequest,
    ):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = auth_service_pb2_grpc.AuthServiceStub(channel)
            response = stub.IsUserAuthenticated(request)
            return response
