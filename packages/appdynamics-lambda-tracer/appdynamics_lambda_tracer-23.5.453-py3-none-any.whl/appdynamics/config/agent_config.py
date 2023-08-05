import asyncio
import json
import logging
import threading
import time

from appdynamics.util.constants import AGENT_CONFIG_INITIAL_FAILURE_TIMEOUT_SECS, \
    AGENT_CONFIG_INITIAL_RETRY_TIMEOUT_SECS, AGENT_CONFIG_RETRY_TIMEOUT_SECS, APPDYNAMICS_LOGGER_NAME, \
    EVENT_TYPE_AGENT_CONFIG, TRACER_LANGUAGE_NAME, X_APPD_API_KEY_HEADER, X_APPD_REQUEST_TYPE_HEADER, \
    X_APPD_ROUTING_KEY_HEADER
from appdynamics.util.tracer_errors import HttpServiceError


class AgentConfig:
    """
    AgentConfig class will handle sending registration requests to the controller.

    Its responsibilities include:
        - Sending requests to controller via http_service.py.
        - Retrying if a failure occurs, until hitting a retry limit.
        - Keep track of last successful request, and send new request every 60 seconds.

    Attributes:
        profiler: Reference to profiler class.
        config: Reference to Config class which contains environment variable details and calculations.
        http_service: Reference to http_service.
        lambda_details: Reference to lambda_details class which holds lambda specific information
        last_updated_time: Timestamp of last successful agent config request made. Initializes at timestamp of init.
        retry_timeout: Time to sleep between agent config invocations.
        logger: Reference to the logger.
        stop_lock: A lock that ensures we do not stop the agent config when we're in the middle of sending a request
            and/or receiving the response.
    """

    def __init__(self, profiler, http_service, config, lambda_details):
        self.profiler = profiler
        self.config = config
        self.http_service = http_service
        self.lambda_details = lambda_details
        self.last_updated_time = time.time()
        self.retry_timeout = AGENT_CONFIG_INITIAL_RETRY_TIMEOUT_SECS
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
        self.event_loop = asyncio.get_event_loop()
        self.stop_lock = threading.Lock()

    """ Send registration request and attempt to retry up to limit upon failure. """
    async def handle_registration(self):
        """
        Send registration request and attempt to retry up to limit upon failure. Will stop when
        profiler.cleanup_event_loop() cancels this task.
        """
        try:
            while self.stop_lock.acquire(blocking=False):
                # Send request if timeout is still initialization default (10 secs) or it has been more than 60 seconds
                # since last attempted request.
                if self.retry_timeout == AGENT_CONFIG_INITIAL_RETRY_TIMEOUT_SECS or \
                        (time.time() - self.last_updated_time) >= self.retry_timeout:

                    response = await self.send_request()
                    if response:
                        self.profiler.agent_config_response.update(response)
                        self.last_updated_time = time.time()
                        self.retry_timeout = AGENT_CONFIG_RETRY_TIMEOUT_SECS
                        self.logger.info(
                            "Successfully sent agent config request.")
                    else:
                        # If retry timeout is equal to initial timeout, we have not sent a successful agent config yet.
                        # If it has also been sixty seconds since we initialized the class, stop sending agent config
                        # every ten seconds and set to normal timeout of sixty seconds.
                        if self.retry_timeout == AGENT_CONFIG_INITIAL_RETRY_TIMEOUT_SECS and \
                                (time.time() - self.last_updated_time) >= AGENT_CONFIG_INITIAL_FAILURE_TIMEOUT_SECS:
                            self.logger.warning(f"Failed to send agent config for past "
                                                f"{AGENT_CONFIG_INITIAL_FAILURE_TIMEOUT_SECS} seconds. "
                                                f"Setting default timeout to {AGENT_CONFIG_RETRY_TIMEOUT_SECS} seconds")
                            self.retry_timeout = AGENT_CONFIG_RETRY_TIMEOUT_SECS
                        else:
                            self.logger.info(f"Failed to send agent config request. Will retry in "
                                             f"{self.retry_timeout} seconds.")
                else:
                    self.logger.debug("No agent_config request required.")
                self.stop_lock.release()
                await asyncio.sleep(self.retry_timeout)
        except asyncio.CancelledError as task_cancel_err:
            self.logger.debug(
                "Agent Config task cancelled. Will no longer send requests")
            try:
                self.stop_lock.release()
            except RuntimeError:
                self.logger.debug("Lock already released.")
            finally:
                raise task_cancel_err

    """ Handles creating the request and its headers, and send to http_service.py """
    async def send_request(self):
        agent_config_request = {
            'account_name': self.config.account_name,
            'application_name': self.config.application_name,
            'tier_name': self.config.tier_name,
            'controller_host': self.config.controller_host,
            'controller_port': self.config.controller_port,
            'language': TRACER_LANGUAGE_NAME,
            'tracer_version': self.config.tracer_version,
            'function_name': self.lambda_details.function_name,
            'function_version': self.lambda_details.function_version,
            'invoked_function_arn': 't_function_arn'
        }
        request_json = json.dumps(agent_config_request)

        headers = {
            "Content-Type": "application/json",
            X_APPD_API_KEY_HEADER: self.config.api_key,
            X_APPD_REQUEST_TYPE_HEADER: EVENT_TYPE_AGENT_CONFIG,
            X_APPD_ROUTING_KEY_HEADER: self.config.routing_key
        }

        response = None
        try:
            response = await self.http_service.post(self.config.agent_config_url, headers, request_json, self.config.http_timeout_secs)
            self.logger.debug(
                f"Successfully received agent config response: {response}")
        except HttpServiceError as e:
            self.logger.warning(
                f"Received error while sending agent config: {e.msg}")
        except Exception as e:
            self.logger.warning(
                f"Raised exception while sending agent config: {e}")
        return response
