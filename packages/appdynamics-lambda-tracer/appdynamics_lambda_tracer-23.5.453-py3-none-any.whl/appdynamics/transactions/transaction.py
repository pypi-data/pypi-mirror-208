import logging
import uuid
from datetime import datetime

from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME
from appdynamics.util.tracer_errors import TransactionValidationError

_logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)


class Transaction:
    def __init__(self, txn_details: dict):
        """The Transaction Class has info about the current business transaction.
        This class is useful when creating transaction events like bt, bt error, exit call, exit call error and so on.
        """
        try:
            validate_txn_details_input(txn_details)
            self.controller_guid = txn_details.get("controller_guid")
            self.skew_adjusted_start_wall_time = txn_details.get(
                "skew_adjusted_start_wall_time")
            self.bt_id = txn_details.get("bt_id") if (
                txn_details.get("bt_id") is not None) else 0
            self.bt_name = txn_details.get("bt_name") if (
                txn_details.get("bt_name") is not None) else None
            self.start_time = txn_details.get("start_time") if (
                txn_details.get("start_time") is not None) else round(datetime.utcnow().timestamp() * 1000)
            self.end_time = ""
            self.request_guid = uuid.uuid4().hex
            self.started = False
            self.caller_chain = ""
            self.corr_header = None
            self.ignore = False
            self.exit_call_counter = 0
        except TransactionValidationError as e:
            raise TransactionValidationError(
                f"Transaction cannot be created. {e.msg}")


def validate_txn_details_input(txn_details: dict) -> bool:
    if txn_details is None:
        _logger.error("Transaction details are missing")
        raise TransactionValidationError("Transaction details are missing")
    #TODO: on cold start events, the controller_guid that is passed in is an empty
    # string which passes validation because it is not None. Is this ok?
    if txn_details.get("controller_guid") is None:
        _logger.error(
            "Controller GUID is missing in the transaction details")
        raise TransactionValidationError(
            "Controller GUID is missing in the transaction details")
    if txn_details.get("skew_adjusted_start_wall_time") is None:
        _logger.error(
            "Skew adjusted wall start time is missing in the transaction details")
        raise TransactionValidationError(
            "Skew adjusted wall start time is missing in the transaction details")
    return True
