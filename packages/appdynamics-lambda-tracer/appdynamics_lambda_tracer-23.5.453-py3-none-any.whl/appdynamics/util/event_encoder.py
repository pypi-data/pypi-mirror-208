import json
import logging

from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME


class EventEncoder(json.JSONEncoder):
    """
    Custom event encoder for the EventService. Requires that events have a __str__() method that will
    return a string-ified json object.

    Throws a type error (via 'json.JSONEncoder.default()') if json.loads() cannot parse the event.
    """
    logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

    def default(self, obj):
        try:
            return obj.__dict__()
        except AttributeError as e:
            EventEncoder.logger.error(f"Unable to encode event object: {e}")
            return json.JSONEncoder.default(self, obj)
