import json
from datetime import datetime

from appdynamics.events.tracer_events import TracerEvents
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.constants import DEFAULT_AGENT_VERSION, ENTRY_POINT_TYPE


class ErrorEvent:
    def __init__(self, current_transaction: Transaction, error_name: str, error_message: str, backend_id: int = 0, http_status_code: int = 0):
        self.event_type = TracerEvents.ERROR_EVENT.value
        self.bt_id = current_transaction.bt_id
        self.backend_id = backend_id
        self.caller_chain = ""
        self.error_name = error_name
        self.error_message = error_message if error_message else "No error message."
        self.version = DEFAULT_AGENT_VERSION
        self.http_status_code = http_status_code
        self.start_time = current_transaction.start_time
        self.end_time = round(datetime.utcnow().timestamp() * 1000)
        self.transaction_guid = current_transaction.request_guid
        # These fields are used for cold start events
        self.entry_point_name = current_transaction.bt_name
        self.entry_point_type = ENTRY_POINT_TYPE

    def __dict__(self):
        return {
            "event_type": self.event_type,
            "bt_id": self.bt_id,
            "backend_id": self.backend_id,
            "caller_chain": self.caller_chain,
            "error_name": self.error_name,
            "error_message": self.error_message,
            "version": self.version,
            "http_status_code": self.http_status_code,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "transaction_guid": self.transaction_guid,
            "entry_point_name": self.entry_point_name,
            "entry_point_type": self.entry_point_type
        }

    def __str__(self):
        return json.dumps(self.__dict__())

    def __eq__(self, other):
        return self.event_type == other.event_type and \
            self.bt_id == other.bt_id and \
            self.backend_id == other.backend_id and \
            self.caller_chain == other.caller_chain and \
            self.error_name == other.error_name and \
            self.error_message == other.error_message and \
            self.version == other.version and \
            self.http_status_code == other.http_status_code and \
            self.start_time == other.start_time and \
            self.end_time == other.end_time and \
            self.transaction_guid == other.transaction_guid and \
            self.entry_point_name == other.entry_point_name and \
            self.entry_point_type == other.entry_point_type
