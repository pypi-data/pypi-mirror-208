from appdynamics.exit_calls.registered_backend_info import RegisteredBackendInfo
from appdynamics.transactions.transaction import Transaction


class ExitCall:
    """
    ExitCall class stores the information regarding an exit call.
    """

    def __init__(self, registered_backend_info: RegisteredBackendInfo, transaction: Transaction):
        self.transaction_guid = transaction.request_guid
        self.bt_id = transaction.bt_id
        self.exit_point_type = registered_backend_info.exit_point_type
        self.exit_point_sub_type = registered_backend_info.exit_point_sub_type
        self.exit_component = None
        self.identifying_properties = registered_backend_info.identifying_properties
        self.backend_id = registered_backend_info.backend_id
        self.start_time = None
        self.end_time = None
        self.started = False
        self.sequence_info = 0


def verify_exit_call(exit_call: ExitCall) -> bool:
    return bool(exit_call) \
        and isinstance(exit_call.transaction_guid, str) \
        and isinstance(exit_call.bt_id, int) \
        and isinstance(exit_call.exit_point_type, str) \
        and isinstance(exit_call.exit_point_sub_type, str) \
        and isinstance(exit_call.identifying_properties, list) \
        and isinstance(exit_call.backend_id, int)
