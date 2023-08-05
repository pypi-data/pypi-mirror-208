import logging
import os
import uuid

from appdynamics.config.agent_config_response import AgentConfigResponse
from appdynamics.eum.eum_cookie import EUMCookie
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.constants import ENV_APPDYNAMICS_ENABLE_EUM, APPDYNAMICS_LOGGER_NAME

class EUM:

    def __init__(self, agent_config_response: AgentConfigResponse):
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

        self.agent_config_response = agent_config_response
        self.global_account_name = ""

        # GUID generation
        self.uuid_base = uuid.uuid4()
        self.next_eum_cookie_id = 1

        self.enabled = False
        if ENV_APPDYNAMICS_ENABLE_EUM in os.environ:
            self.enabled = os.environ[ENV_APPDYNAMICS_ENABLE_EUM].strip().lower() == "true"

    def generate_guid(self) -> str:
        guid_int = self.uuid_base.int + self.next_eum_cookie_id
        self.next_eum_cookie_id += 1
        guid = uuid.UUID(int=guid_int)
        return str(guid)

    def get_global_account_name(self) -> str:
        if not self.global_account_name:
            self.global_account_name = self.agent_config_response.global_account_name

        return self.global_account_name

    def should_inject_eum(self, transaction: Transaction, lambda_event: dict) -> bool:
        """
        Should add eum headers to response if:
         1. APPDYNAMICS_ENABLE_EUM environment variable is set
         2. Transaction is originating transaction
         3. Lambda invocation is API gateway call.
         4. Lambda invocation doesn't return an error (this check is handled in the tracer wrapper)
        """
        is_originating_transaction = transaction is not None and transaction.corr_header is None

        return self.enabled and is_originating_transaction

    def new_eum_cookie(self, transaction: Transaction, request_headers: dict, lambda_response: dict) -> EUMCookie:
        return EUMCookie(self, transaction, request_headers, lambda_response)

    def run_eum(self, transaction: Transaction, lambda_event: dict, lambda_response: dict):
        try:
            if self.should_inject_eum(transaction, lambda_event):
                request_headers = lambda_event.get("headers", None)
                eum_cookie = self.new_eum_cookie(transaction, request_headers, lambda_response)
                eum_cookie.build()
        except Exception as exception:
            self.logger.debug("EUM instance has encountered the following error:")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception(exception)
