import logging
import os
from datetime import datetime

from appdynamics.events.bt_event import BtEvent
from appdynamics.events.bt_registration_event import BtRegistrationEvent
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, DEFAULT_AGENT_VERSION, ENTRY_POINT_TYPE
from appdynamics.util.tracer_errors import CorrelationHeaderError, TransactionValidationError


class TransactionService:
    def __init__(self, lambda_details, transaction_registry, event_service):
        self.lambda_details = lambda_details
        self.transaction_registry = transaction_registry
        self.event_service = event_service
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

    def create_transaction(self, txn_details):
        transaction_ins = None
        try:
            transaction_ins = Transaction(txn_details)
            transaction_ins.bt_name = self.get_transaction_name()
        except TransactionValidationError as e:
            self.logger.error(
                f"Failed in creating the transaction due to {str(e)}")
        return transaction_ins

    def start_transaction(self, txn, corr_header=None):
        if txn is None:
            self.logger.error(
                "Failed in starting the transaction. Transaction object is missing")
            return

        if not isinstance(txn, Transaction):
            self.logger.error(
                "Failed in starting the transaction. Passed transaction input is not of type Transaction.")
            return

        if txn.started:
            self.logger.info(
                "Transaction has already been started.")
            return

        if not corr_header:
            # Start originating txn
            self.make_originating_txn(txn)
        else:
            txn.corr_header = corr_header
            if not corr_header.txn_detect:
                self.logger.debug(
                    "Transaction detection is disabled from upstream tier.")
                txn.ignore = True
                txn.started = False
                return
            elif not corr_header.header_string_valid:
                # Start originating txn
                self.logger.debug("Incoming correlation header is not valid.")
                self.make_originating_txn(txn)
            elif corr_header.cross_app_correlation:
                self.logger.debug(
                    "Incoming correlation header is from cross app.")
                self.make_originating_txn(txn)
                txn.caller_chain = corr_header.get_caller_chain()
            else:
                self.logger.debug(
                    "Incoming correlation header is from same application.")
                self.make_continuing_txn(txn, corr_header)

    def make_originating_txn(self, txn: Transaction) -> None:
        # Determine if the transaction is registered or not.
        txn_id = self.transaction_registry.get_bt_id(
            txn.bt_name, ENTRY_POINT_TYPE)

        if not txn_id:
            overflow_txn_id = self.transaction_registry.get_overflow_bt()
            if overflow_txn_id:
                txn_id = overflow_txn_id

        # transaction registration
        if not txn_id:
            # add txn registration event to queue
            bt_registration_event = BtRegistrationEvent(
                txn.bt_name, ENTRY_POINT_TYPE, DEFAULT_AGENT_VERSION)
            self.event_service.add_event(bt_registration_event)

        # Start the transaction; if it's a cold start event, the bt_id will be populated by the backend.
        self.logger.info(
            "Starting the business transaction.")
        txn.started = True
        txn.start_time = round(datetime.utcnow().timestamp() * 1000)
        txn.bt_id = txn_id

    def make_continuing_txn(self, txn, corr_header):
        try:
            corr_header.update_txn_for_continuing_txn(txn)
            txn.started = True
            txn.start_time = round(datetime.utcnow().timestamp() * 1000)
        except CorrelationHeaderError as e:
            self.logger.error(
                f"Received error while creating continuing txn {e.msg}. Creating originating txn now.")
            self.make_originating_txn(txn)

    def stop_transaction(self, txn):
        if not txn:
            self.logger.error(
                "Failed to stop the transaction. Transaction object is missing")
            return

        if not isinstance(txn, Transaction):
            self.logger.error(
                "Failed to stop the transaction. Transaction object is not valid")
            return

        if not txn.started:
            self.logger.info(
                "Transaction has already been stopped")
            return

        # Stop the transaction and create a BT event
        self.logger.info(
            "Stopping the business transaction.")
        txn.started = False
        txn.end_time = round(datetime.utcnow().timestamp() * 1000)

        bt_event = BtEvent()
        bt_event.update_with_transaction_object(txn)
        self.event_service.add_event(bt_event)
        self.logger.debug(
            f"Created and added a BT event to the event service: '{bt_event}'.")
        self.event_service.send_events_downstream()

    def get_transaction_name(self):
        if os.getenv("APPDYNAMICS_DEFAULT_BT_NAME") is not None:
            return os.getenv("APPDYNAMICS_DEFAULT_BT_NAME")
        else:
            return self.lambda_details.function_name + '_' + self.lambda_details.function_version
