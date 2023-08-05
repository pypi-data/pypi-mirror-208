import json

from appdynamics.events.tracer_events import TracerEvents
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.constants import DEFAULT_AGENT_VERSION, ENTRY_POINT_TYPE
from appdynamics.util.tracer_errors import TracerEventError


class BtEvent:
    """
    Class which creates a business transaction event.
    """

    def __init__(self):
        self.event_type = TracerEvents.BT_EVENT.value
        self.bt_id = 0
        self.transaction_guid = ""
        self.start_time = None
        self.end_time = None
        self.caller_chain = ""
        self.version = DEFAULT_AGENT_VERSION
        # These fields are used for cold start events
        self.entry_point_name = ""
        self.entry_point_type = ""

    def update_with_transaction_object(self, transaction: Transaction) -> None:
        """
        Updates the attributes of a BTEvent from a Transaction class instance.
        Args:
            transaction: Instance of a Transaction class
        """
        if transaction and isinstance(transaction, Transaction):
            self.bt_id = transaction.bt_id
            self.entry_point_name = transaction.bt_name
            self.entry_point_type = ENTRY_POINT_TYPE
            self.transaction_guid = transaction.request_guid
            self.start_time = transaction.start_time
            self.end_time = transaction.end_time
            self.caller_chain = transaction.caller_chain
            return

        raise TracerEventError(
            "Updating BT Event failed due to empty or invalid transaction object.")

    def __dict__(self):
        return {
            "event_type": self.event_type,
            "bt_id": self.bt_id,
            "transaction_guid": self.transaction_guid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "caller_chain": self.caller_chain,
            "version": self.version,
            "entry_point_name": self.entry_point_name,
            "entry_point_type": self.entry_point_type
        }

    def __str__(self):
        return json.dumps(self.__dict__())
