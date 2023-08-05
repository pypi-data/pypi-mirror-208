import json

from appdynamics.events.tracer_events import TracerEvents


class ExitCallEvent:
    def __init__(self, bt_id, txn_guid, start_time, end_time, backend_state, backend_id, caller_chain, version):
        self.event_type = TracerEvents.EXIT_CALL_EVENT.value
        self.bt_id = bt_id
        self.transaction_guid = txn_guid
        self.start_time = start_time
        self.end_time = end_time
        self.backend_state = backend_state
        self.backend_id = backend_id
        self.caller_chain = caller_chain
        self.version = version

    def __dict__(self):
        return {
            "event_type": self.event_type,
            "bt_id": self.bt_id,
            "transaction_guid": self.transaction_guid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "backend_state": self.backend_state,
            "backend_id": self.backend_id,
            "caller_chain": self.caller_chain,
            "version": self.version
        }

    def __str__(self):
        return json.dumps(self.__dict__())
