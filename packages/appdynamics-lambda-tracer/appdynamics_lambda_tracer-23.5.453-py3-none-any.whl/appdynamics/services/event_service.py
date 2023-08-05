"""
  Event Service keeps the queue of events that need to be sent
  downstream. On call, it can flush all the events in the queue
  downstream.
"""
import datetime
import json
import logging
import os

from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, ENV_APPDYNAMICS_EVENTS_FLUSH_PERIOD_MS, \
    FLUSH_REFRESH_TIME_IN_MS, X_APPD_API_KEY_HEADER, X_APPD_ROUTING_KEY_HEADER
from appdynamics.util.event_encoder import EventEncoder


class EventService:
    def __init__(self, profiler, config, http_service):
        self.profiler = profiler
        self.config_ins = config
        self.http_service = http_service
        self.events_list = []
        self.last_flush_timestamp = None
        self.events_flush_timedelta = self._get_flush_period()
        self.now = datetime.datetime.now
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
        self.contains_cold_start_event = False
    
    def _get_flush_period(self):
        flush_period = os.getenv(ENV_APPDYNAMICS_EVENTS_FLUSH_PERIOD_MS)
        if flush_period:
            try:
                flush_period_int = int(flush_period)
                return datetime.timedelta(milliseconds=flush_period_int)
            except (TypeError, ValueError):
                self.logger.error(f"{ENV_APPDYNAMICS_EVENTS_FLUSH_PERIOD_MS} should be a number")
        return datetime.timedelta(milliseconds=FLUSH_REFRESH_TIME_IN_MS)

    def add_event(self, event):
        if hasattr(event, "bt_id") and event.bt_id == 0:
            self.contains_cold_start_event = True
        self.events_list.append(event)

    def reset(self):
        del self.events_list[:]
        self.contains_cold_start_event = False

    def print_events(self):
        self.logger.info(
            "Total number of items in the events queue are %d", len(self.events_list))
        if len(self.events_list) > 0:
            self.logger.debug("Events are \n%s",
                              ("\n".join(map(str, self.events_list))))

    def send_events_downstream(self):
        current_time = self.now()
        if self.contains_cold_start_event or self.last_flush_timestamp is None or \
            current_time - self.last_flush_timestamp > self.events_flush_timedelta:
            try:
                events_downstream_url = self.config_ins.events_url
                headers = {
                    "Content-Type": "application/json",
                    X_APPD_API_KEY_HEADER: self.config_ins.api_key,
                    X_APPD_ROUTING_KEY_HEADER: self.config_ins.routing_key
                }
                payload = json.dumps(self.events_list, cls=EventEncoder)
                self.logger.debug(f"Headers for event service is: '{headers}'.")
                self.logger.debug(f"Payload for event service is: '{payload}'.")
                self.print_events()

                self.profiler.add_new_task(
                    self.http_service.post, url=events_downstream_url, headers=headers, payload=payload, connection_timeout=self.config_ins.http_timeout_secs)
                self.logger.info(
                    "Successfully scheduled the sending of events to downstream")
            except Exception as error:
                self.logger.error(f"Error in sending the events downstream due to {error}")
            else:
                self.reset()
            finally:
                self.last_flush_timestamp = self.now()
