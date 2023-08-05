class RegisteredBackendInfo:
    """
    RegisteredBackendInfo class stores the information of a registered backend.
    """

    def __init__(self, exit_point_type, exit_point_sub_type, identifying_properties, backend_id, resolved_entity_type,
                 resolved_entity_id):
        self.exit_point_type = exit_point_type
        self.exit_point_sub_type = exit_point_sub_type
        self.backend_id = backend_id
        self.identifying_properties = identifying_properties
        self.resolved_entity_type = resolved_entity_type
        self.resolved_entity_id = resolved_entity_id
        self.federated_app_id = None
        self.federated_account_guid = None

    def __eq__(self, other):  # For the sake of unit tests.
        return (self.exit_point_type == other.exit_point_type and
                self.exit_point_sub_type == other.exit_point_sub_type and
                self.identifying_properties == other.identifying_properties and
                self.backend_id == other.backend_id and
                self.resolved_entity_type == other.resolved_entity_type and
                self.resolved_entity_id == other.resolved_entity_id and
                self.federated_app_id == other.federated_app_id and
                self.federated_account_guid == other.federated_account_guid)


def generate_registered_backend_info(backend):
    backend_info = RegisteredBackendInfo(backend["exit_point_type"], backend["exit_point_sub_type"],
                                         backend["identifying_properties"], backend["backend_id"],
                                         backend["resolved_entity_type"], backend["resolved_entity_id"])
    # Used explicitly for the federated app component type.
    if "federated_app_id" in backend and "federated_account_guid" in backend:
        backend_info.federated_app_id = backend["federated_app_id"]
        backend_info.federated_account_guid = backend["federated_account_guid"]
    return backend_info
