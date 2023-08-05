import logging

from appdynamics.events.backend_registration_event import BackendRegistrationEvent
from appdynamics.exit_calls.exit_call import ExitCall
from appdynamics.exit_calls.exit_component import ExitComponent, ExitFederatedAppComponent, ExitForeignAppComponent, \
    UnresolvedExitComponent
from appdynamics.exit_calls.registered_backend_info import RegisteredBackendInfo
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME
from datetime import datetime


class ExitCallService:
    """
    ExitCallService class provides methods to create, start and stop an exit call.

    Attributes:
        backend_registry: Instance of BackendRegistry class. It is used to store and retrieve registered backends.
        event_service: Instance of EventService class. It is used to add and flush events to the serverless backend
        logger: Reference to the in-build logging service.
    """

    def __init__(self, backend_registry, event_service):
        self.backend_registry = backend_registry
        self.event_service = event_service
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

    def create_exit_call(self, exit_point_type, exit_point_sub_type, identifying_properties, current_transaction):
        """
        Creates the current exit call.

        Returns:
            current_exit_call: Valid exit call object when the exit call's backend is registered with the controller.
            None: If the backend is yet to be registered.
        """
        if exit_point_type and exit_point_sub_type and identifying_properties and isinstance(current_transaction,
                                                                                             Transaction):
            identifying_properties = convert_identifying_properties_to_prop_val(identifying_properties)
            registered_backend_info = self.backend_registry.get_registered_backend_info(exit_point_type,
                                                                                        exit_point_sub_type,
                                                                                        identifying_properties)
            if isinstance(registered_backend_info, RegisteredBackendInfo):
                self.logger.debug("Creating the exit call object with backend.")
                current_exit_call = ExitCall(registered_backend_info, current_transaction)
                return current_exit_call
            else:
                self.logger.debug("Registering the backend with the controller.")
                backend_registration_event = BackendRegistrationEvent(exit_point_type, exit_point_sub_type,
                                                                      identifying_properties)
                self.event_service.add_event(backend_registration_event)
        else:
            self.logger.error("Exit point type, subtype, identifying properties, or current transaction is not "
                              "defined.")

    def start(self, exit_call):
        exit_call.start_time = round(datetime.utcnow().timestamp() * 1000)
        backend_info = self.backend_registry.get_registered_backend_info(exit_call.exit_point_type,
                                                                         exit_call.exit_point_sub_type,
                                                                         exit_call.identifying_properties)
        if backend_info.resolved_entity_type == "COMPONENT":
            exit_call.exit_component = ExitComponent(exit_call.backend_id, backend_info.resolved_entity_id)
        elif backend_info.resolved_entity_type == "FOREIGN_APP":
            exit_call.exit_component = ExitForeignAppComponent(exit_call.backend_id, backend_info.resolved_entity_id)
        elif backend_info.resolved_entity_type == "FEDERATED_APP":
            exit_call.exit_component = ExitFederatedAppComponent(exit_call.backend_id, backend_info.federated_app_id,
                                                                 backend_info.federated_account_guid)
        elif backend_info.resolved_entity_type == "UNRESOLVED":
            exit_call.exit_component = UnresolvedExitComponent(exit_call.backend_id)
        else:
            self.logger.warning("Exit call entity type is unknown. Leaving exit call component type as None.")


def convert_identifying_properties_to_prop_val(identifying_properties):
    """
    Agent API and agent config response use [{"property": prop1, "value": val1}, {"property: prop2, "value": val2}].
    Convert the input identifying properties to match this.

    :param identifying_properties: Identifying properties in format {"prop1" : "val1", "prop2": "val2"}.
    :return: The converted identifying properties
    """
    return [{"property": k, "value": v} for k, v in identifying_properties.items()]
