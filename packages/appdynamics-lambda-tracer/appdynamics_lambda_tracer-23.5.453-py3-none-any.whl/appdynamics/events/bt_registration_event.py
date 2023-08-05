import json

from appdynamics.events.tracer_events import TracerEvents


class BtRegistrationEvent:
    """
      BtRegistrationEvent creates an event for business transaction registration.
    """

    def __init__(self, entry_point_name, entry_point_type, tracer_version):
        self.event_type = TracerEvents.REGISTRATION_BT_EVENT.value
        self.entry_point_name = entry_point_name
        self.entry_point_type = entry_point_type
        self.version = tracer_version

    def __dict__(self):
        return {
            "entry_point_name": self.entry_point_name,
            "entry_point_type": self.entry_point_type,
            "event_type": self.event_type,
            "version": self.version
        }

    def __str__(self):
        return json.dumps(self.__dict__())
