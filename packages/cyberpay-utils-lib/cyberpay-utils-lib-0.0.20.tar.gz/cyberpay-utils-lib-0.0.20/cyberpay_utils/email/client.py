import grpc

from .proto import email_pb2, email_pb2_grpc


class EmailServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def send_close_document_email(
        self, request: email_pb2.SendCloseDocumentEmailRequest
    ):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendCloseDocumentEmail(request)
            return response

    def send_contract_email(self, request: email_pb2.SendContractEmailRequest):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendContractEmail(request)
            return response

    def send_login_password_email(
        self, request: email_pb2.SendLoginPasswordEmailRequest
    ):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendLoginPasswordEmail(request)
            return response

    def send_new_employee_email(self, request: email_pb2.SendNewEmployeeEmailRequest):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendNewEmployeeEmail(request)
            return response

    def send_new_support_request_email(
        self, request: email_pb2.SendNewSupportRequestEmailRequest
    ):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendNewSupportRequestEmail(request)
            return response

    def send_new_task_email(self, request: email_pb2.SendNewTaskEmailRequest):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendNewTaskEmail(request)
            return response

    def send_otp_code_email(self, request: email_pb2.SendOtpCodeEmailRequest):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendOtpCodeEmail(request)
            return response

    def send_reset_password_email(
        self, request: email_pb2.SendResetPasswordEmailRequest
    ):
        with grpc.insecure_channel(self.service_host) as channel:
            stub = email_pb2_grpc.EmailStub(channel)
            response = stub.SendResetPasswordEmail(request)
            return response
