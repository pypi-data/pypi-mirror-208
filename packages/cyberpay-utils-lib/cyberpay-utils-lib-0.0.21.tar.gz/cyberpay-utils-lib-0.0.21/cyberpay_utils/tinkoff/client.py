import grpc
from google import protobuf as google_proto

from .proto import (
    accept_deal_pb2,
    add_deponent_to_deal_step_pb2,
    add_recipient_to_deal_step_pb2,
    complete_deal_step_pb2,
    create_beneficiary_bank_details_pb2,
    create_deal_pb2,
    create_step_in_deal_pb2,
    edit_beneficiary_bank_details_pb2,
    edit_beneficiary_pb2,
    get_bank_statement_pb2,
    get_deal_is_valid_pb2,
    get_deal_step_by_id_pb2,
    get_incoming_transactions_pb2,
    get_virtual_accounts_balances_pb2,
    identify_incoming_transaction_pb2,
    json_data_pb2,
    tinkoff_pb2_grpc,
)


class TinkoffServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def get_bank_statement(
        self, request: get_bank_statement_pb2.GetBankStatementRequest
    ) -> get_bank_statement_pb2.GetBankStatementResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.GetBankStatement(request)
            return response

    def get_deal_is_valid(
        self, request: get_deal_is_valid_pb2.GetDealIsValidRequest
    ) -> get_deal_is_valid_pb2.GetDealIsValidResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.GetDealIsValid(request)
            return response

    def get_deal_step_by_id(
        self, request: get_deal_step_by_id_pb2.GetDealStepByIDRequest
    ) -> get_deal_step_by_id_pb2.GetDealStepByIDResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.GetDealStepByID(request)
            return response

    def get_incoming_transactions(
        self, request: get_incoming_transactions_pb2.GetIncomingTransactionsRequest
    ) -> get_incoming_transactions_pb2.GetIncomingTransactionsResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.GetIncomingTransactions(request)
            return response

    def get_virtual_accounts_balances(
        self,
        request: get_virtual_accounts_balances_pb2.GetVirtualAccountsBalancesRequest,
    ) -> get_virtual_accounts_balances_pb2.GetVirtualAccountsBalancesResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.GetVirtualAccountsBalances(request)
            return response

    def accept_deal(
        self,
        request: accept_deal_pb2.AcceptDealRequest,
    ) -> google_proto.empty_pb2.Empty:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.AcceptDeal(request)
            return response

    def add_deponent_to_deal_step(
        self,
        request: add_deponent_to_deal_step_pb2.AddDeponentToDealStepRequest,
    ) -> add_deponent_to_deal_step_pb2.AddDeponentToDealStepResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.AddDeponentToDealStep(request)
            return response

    def add_recipient_to_deal_step(
        self,
        request: add_recipient_to_deal_step_pb2.AddRecipientToDealStepRequest,
    ) -> add_recipient_to_deal_step_pb2.AddRecipientToDealStepResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.AddRecipientToDealStep(request)
            return response

    def complete_deal_step(
        self,
        request: complete_deal_step_pb2.CompleteDealStepRequest,
    ) -> google_proto.empty_pb2.Empty:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.CompleteDealStep(request)
            return response

    def create_deal(
        self,
        request: create_deal_pb2.CreateDealRequest,
    ) -> create_deal_pb2.CreateDealResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.CreateDeal(request)
            return response

    def create_step_in_deal(
        self,
        request: create_step_in_deal_pb2.CreateStepInDealRequest,
    ) -> create_step_in_deal_pb2.CreateStepInDealResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.CreateStepInDeal(request)
            return response

    def identify_incoming_transaction(
        self,
        request: identify_incoming_transaction_pb2.IdentifyIncomingTransactionRequest,
    ) -> google_proto.empty_pb2.Empty:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.IdentifyIncomingTransaction(request)
            return response

    def create_beneficiary_bank_details(
        self,
        request: create_beneficiary_bank_details_pb2.CreateBeneficiaryBankDetailsRequest,
    ) -> json_data_pb2.JsonData:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.CreateBeneficiaryBankDetails(request)
            return response

    def edit_beneficiary_bank_details(
        self,
        request: edit_beneficiary_bank_details_pb2.EditBeneficiaryBankDetailsRequest,
    ) -> json_data_pb2.JsonData:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.EditBeneficiaryBankDetails(request)
            return response

    def create_beneficiary(
        self,
        request: json_data_pb2.JsonData,
    ) -> json_data_pb2.JsonData:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.CreateBeneficiary(request)
            return response

    def edit_beneficiary(
        self,
        request: edit_beneficiary_pb2.EditBeneficiaryRequest,
    ) -> json_data_pb2.JsonData:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = tinkoff_pb2_grpc.TinkoffStub(channel)
            response = stub.EditBeneficiary(request)
            return response
