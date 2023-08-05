import enum


class TracerEvents(enum.Enum):
    """
      TracerEvents hold values for different types of tracer
      events.
    """
    BT_EVENT = "BT"
    EXIT_CALL_EVENT = "EXIT_CALL"
    ERROR_EVENT = "ERROR"
    REGISTRATION_BT_EVENT = "REGISTRATION_BT"
    REGISTRATION_BACKEND_EVENT = "REGISTRATION_BACKEND"
