from datetime import datetime
from typing import Any, Callable

import grpc
from google.protobuf.message import Message
from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException


class GRPCLoggingRequestsInterceptor(ServerInterceptor):
    """Interceptor for logging gRPC requests"""

    def intercept(
        self,
        method: Callable,
        request: Message,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        print(
            "gRPC Request",
            datetime.now(),
            method_name,
            sep=" | ",
        )
        return method(request, context)


class GRPCLoggingExceptionsInterceptor(ServerInterceptor):
    """Interceptor for logging exceptions"""

    def intercept(
        self,
        method: Callable,
        request: Message,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            return method(request, context)

        except GrpcException as exception:
            print(
                "gRPC Exception:",
                datetime.now(),
                method_name,
                exception.status_code,
                exception.details,
                sep=" | ",
            )
            context.set_code(exception.status_code)
            context.set_details(exception.details)
            raise exception

        except Exception as exception:
            print(
                "gRPC Exception:",
                datetime.now(),
                method_name,
                "Unknown exception:",
                exception,
                sep=" | ",
            )
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Unknown exception occurred")
            raise exception
