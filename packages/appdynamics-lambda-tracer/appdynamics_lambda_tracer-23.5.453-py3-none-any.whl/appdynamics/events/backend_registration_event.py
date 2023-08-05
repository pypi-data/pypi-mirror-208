import json

from appdynamics.events.tracer_events import TracerEvents
from appdynamics.util.constants import DEFAULT_AGENT_VERSION


class BackendRegistrationEvent:
    """
    BackendRegistrationEvent creates an event for backend registration with the controller.

    Attributes:
        event_type: Tracer event type.
        exit_point_type: Type of the exit call. Ex: HTTP
        exit_point_sub_type: Sub type of the exit call, if it exists. Else it's the same as exit_point_type.
        identifying_properties: Properties of the exit call. Ex: For HTTP calls, it could contain properties like the host and port.
        version: Tracer version.
    """

    def __init__(self, exit_point_type, exit_point_sub_type, identifying_properties, tracer_version=DEFAULT_AGENT_VERSION):
        self.event_type = TracerEvents.REGISTRATION_BACKEND_EVENT.value
        self.exit_point_type = exit_point_type
        self.exit_point_sub_type = exit_point_sub_type
        self.identifying_properties = identifying_properties
        self.version = tracer_version

    def __dict__(self):
        return {
            "event_type": self.event_type,
            "exit_point_type": self.exit_point_type,
            "exit_point_sub_type": self.exit_point_sub_type,
            "identifying_properties": self.identifying_properties,
            "version": self.version
        }

    def __str__(self):
        return json.dumps(self.__dict__())
