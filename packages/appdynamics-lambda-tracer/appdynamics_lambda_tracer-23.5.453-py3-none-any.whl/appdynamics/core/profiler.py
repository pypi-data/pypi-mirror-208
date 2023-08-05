import asyncio
import logging
import threading
from datetime import datetime
from typing import Any, Union

from appdynamics.config import AgentConfig, AgentConfigResponse
from appdynamics.correlation.correlation_header import CorrelationHeader
from appdynamics.eum.eum import EUM
from appdynamics.events.error_event import ErrorEvent
from appdynamics.events.exit_call_event import ExitCallEvent
from appdynamics.exit_calls.backend_registry import BackendRegistry
from appdynamics.exit_calls.exit_call import ExitCall, verify_exit_call
from appdynamics.exit_calls.exit_call_service import ExitCallService
from appdynamics.services.event_service import EventService
from appdynamics.services.http_service import HttpService
from appdynamics.services.transaction_service import TransactionService
from appdynamics.transactions.transaction import Transaction
from appdynamics.transactions.transaction_registry import TransactionRegistry
from appdynamics.util.config import Config, fetch_log_level
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, DEFAULT_AGENT_VERSION
from appdynamics.util.lambda_details import LambdaDetails

_logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
_logger.setLevel(fetch_log_level())
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s AppDynamics - %(filename)s [%(levelname)s]: %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)
_logger.propagate = False
_profiler = None


def init():
    """
    Initialize profiler and logger if they don't exist.

    Returns:
        profiler: Returns Profiler class or a NoOpProfiler if a failure occurs during Profiler.__init__.
    """
    global _logger, _profiler

    if not _profiler or isinstance(_profiler, NoOpProfiler):
        try:
            _profiler = Profiler()
        except Exception as e:
            _profiler = NoOpProfiler()
            _logger.error("Will use NoOpTracer. Could not initialize environment variables correctly due to error: "
                          f"\"{e}\" ")
    return _profiler


class Profiler:
    """
    Class containing the core of the tracer code.

    tracer.py acts as a wrapper while this class contains all code necessary for operation of the tracer.
    Profiler will contain references to all of our services and agent config, and handle the starting and stopping
    of transactions.

    Attributes:
        current_transaction: Instance of the Transaction class where various properties of a business transaction is
            stored. This holds the current or ongoing business transaction.
        http_service: Reference to HttpService class.
        agent_config_response: Reference to AgentConfigResponse class.
        config: Reference to Config class which contains environment variable details and calculations.
        agent_config: Reference to AgentConfig class.
        transaction_registry: Reference to TransactionRegistry class where registered transaction details are kept.
        backend_registry: Reference to BackendRegistry class where registered backends' details are kept.
        event_service: Reference to EventService class which takes care of flushing the tracer events.
        lambda_details: Reference to LambdaDetails class which contains lambda function details.
        transaction_service: Reference to TransactionService class.
        exit_call_service: Reference to ExitCallService class. It carries out useful exit call operations.
        _event_loop: The event loop started in initialize_event_loop() that will be shared between threads.
        _concurrent_futures: List of pending concurrent futures that we'll need to await if the result has not already
            returned upon cleanup. NOTE: this list should only contain futures of type concurrent.futures.Future and
            __NOT__ of type asyncio.Future. In cleanup_event_loop(), we use call future.result() which will block in
            the concurrent.futures variation but potentially throw a runtime error in the asyncio.Future variation.
        _thread: Reference to new thread generated. Used to cleanup thread.
    """

    def __init__(self):
        self.current_transaction = None
        self.http_service = HttpService()
        self.transaction_registry = TransactionRegistry()
        self.backend_registry = BackendRegistry()
        self.agent_config_response = AgentConfigResponse(
            self.transaction_registry, self.backend_registry)
        self.config = Config()
        self.event_service = EventService(self, self.config, self.http_service)
        self.lambda_details = LambdaDetails()
        self.agent_config = AgentConfig(
            self, self.http_service, self.config, self.lambda_details)
        self.transaction_service = TransactionService(
            self.lambda_details, self.transaction_registry, self.event_service)
        self.exit_call_service = ExitCallService(
            self.backend_registry, self.event_service)
        self.eum = EUM(self.agent_config_response)
        self._event_loop = None
        self._concurrent_futures = []
        self._thread = None

    def create_thread(self) -> None:
        """
        Method will be run upon every call to start_bt(). Threading work handled here instead of upon __init__, so that
        we can reuse the profiler between invocations.

        Spawns initialize_event_loop() in a new thread.
        """
        if self._thread and self._thread.is_alive():
            _logger.warning(
                "Profiler thread already exists. Will not spawn a new thread.")
        else:
            self._event_loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self.initialize_event_loop)
            self._thread.start()

    def initialize_event_loop(self) -> None:
        """
        Method will be run in a different thread and is in charge of setting up the thread's event loop and sending
        the first agent config request.

        This thread and event loop will be used for all of our asynchronous needs and will be isolated from the
        customer event loops.
        """
        asyncio.set_event_loop(self._event_loop)
        asyncio.ensure_future(self.agent_config.handle_registration())
        try:
            self._event_loop.run_forever()
        finally:
            self._event_loop.close()

    def add_new_task(self, task: Any, *args: Any, **kwargs: Any) -> None:
        """
        Function that allows us to easily add new task to the running event loop. Coroutine type expected for
        task parameter.
        """
        if self._event_loop and self._event_loop.is_running():
            fut = asyncio.run_coroutine_threadsafe(
                task(*args, **kwargs), self._event_loop)
            self._concurrent_futures.append(fut)
        else:
            _logger.warning(
                "Event loop is not running. Will not enqueue task.")

    def get_eum_instance(self) -> EUM:
        """
        Gets the current eum instance
        Returns:
            eum: Current eum instance that is in charge of injecting eum headers
        """
        return self.eum

    def set_current_transaction(self, transaction: Transaction) -> None:
        """
        Sets the current_transaction attribute with a valid transaction instance.
        Args:
            transaction: Instance of Transaction class
        """
        if transaction and isinstance(transaction, Transaction):
            self.current_transaction = transaction
            return

        raise TypeError("Error setting the current transaction. Transaction is either null or not a valid instance of "
                        "the Transaction Class.")

    def get_current_transaction(self) -> Transaction:
        """
        Gets the current_transaction attribute.
        Returns:
            current_transaction: Current business transaction which is an instance of Transaction class
        """
        return self.current_transaction

    def reset_current_transaction(self) -> None:
        """
        Resets the current_transaction to None
        """
        self.current_transaction = None

    def has_transaction_started(self) -> bool:
        """
        Checks if a business transaction has been started.
        Returns:
            True, if the transaction is started else False.
        """
        current_txn = self.current_transaction
        return bool(current_txn) and isinstance(current_txn, Transaction) and current_txn.started

    def start_bt(self, lambda_event: Any, lambda_context: Any) -> None:
        """
        Starts the current business transaction.
        """
        try:
            self.create_thread()

            if self.has_transaction_started():
                _logger.info("Transaction has already started.")
                return

            # create a transaction object
            if self.agent_config_response.last_update_time_stamp is None:
                #TODO: is this necessary?
                _logger.debug(
                    "Agent config response does not exist. Creating cold start transaction")
            else:
                _logger.debug(
                    "Agent config response exists. Going to create the transaction")
                    
            txn_details = {
                "controller_guid": self.agent_config_response.controller_guid,
                "start_time": round(datetime.utcnow().timestamp() * 1000),
                "skew_adjusted_start_wall_time": self.agent_config_response.get_skew_adjusted_start_wall_time()
            }
            current_transaction = self.transaction_service.create_transaction(
                txn_details)

            if current_transaction and isinstance(current_transaction, Transaction):
                incoming_corr_header = self.lambda_details.get_correlation_header_value(
                    lambda_event, lambda_context)
                corr_header = None
                if incoming_corr_header:
                    _logger.debug(
                        f"Incoming correlation header found. Its value is {incoming_corr_header}")
                    corr_header = CorrelationHeader(
                        self.agent_config_response, header_string=incoming_corr_header)
                self.transaction_service.start_transaction(
                    current_transaction, corr_header=corr_header)
                self.set_current_transaction(current_transaction)

        except Exception as e:
            _logger.error(f"Error while starting BT in profiler: {e}")

    def stop_bt(self) -> None:
        """
        Stops the current business transaction.
        """
        try:
            current_transaction = self.get_current_transaction()
            if not (current_transaction and isinstance(current_transaction, Transaction)):
                _logger.info("No valid transaction to be stopped.")
                return

            if not self.has_transaction_started():
                _logger.info("Transaction already stopped.")
                return

            self.transaction_service.stop_transaction(current_transaction)

        except Exception as e:
            _logger.error(
                f"Error occurred while stopping the transaction: {e}")
        finally:
            self.reset_current_transaction()
            self.cleanup_event_loop()

    def start_exit_call(self, exit_point_type: str, exit_point_sub_type: str, identifying_properties: dict) -> ExitCall:
        """
        Starts the exit call.

        Args:
            exit_point_type: Type of the exit call. Ex: HTTP
            exit_point_sub_type: Sub type of the exit call, if it exists. Else it's the same as exit_point_type.
            identifying_properties: Properties of the exit call. Ex: For HTTP calls, it could contain properties like
                the host and port.

        Returns:
            current_exit_call: It's an exit call object which contains the information of the registered backend as
                well as the exit call metrics.
        """
        try:
            if not (exit_point_type and exit_point_sub_type and identifying_properties):
                missing_properties = []
                if not exit_point_type:
                    missing_properties.append("exit_point_type")
                if not exit_point_sub_type:
                    missing_properties.append("exit_point_sub_type")
                if not identifying_properties:
                    missing_properties.append("identifying_properties")
                _logger.error(f"Can't create exit call. Missing required exit call properties: '"
                              f"{', '.join(missing_properties)}'.")

            elif not self.get_current_transaction() or not isinstance(self.get_current_transaction(), Transaction):
                _logger.info(
                    "No valid transaction. Will not create exit call and return None.")

            elif not self.has_transaction_started():
                _logger.info(
                    "Transaction already stopped. Will not create exit call and return None.")
            
            elif not self.get_current_transaction().bt_id:
                _logger.info(
                    "Transaction does not have a valid BT id. Assuming cold start transaction. Will not create exit call and return None.")

            else:
                _logger.debug(f"Creating exit call with exit point type: '{exit_point_type}', exit point subtype: "
                              f"'{exit_point_sub_type}', and identifying properties: '{identifying_properties}'.")
                current_exit_call = self.exit_call_service.create_exit_call(exit_point_type, exit_point_sub_type,
                                                                            identifying_properties,
                                                                            self.current_transaction)
                if current_exit_call and isinstance(current_exit_call, ExitCall):
                    self.exit_call_service.start(current_exit_call)
                    current_transaction = self.get_current_transaction()
                    current_transaction.exit_call_counter += 1
                    current_exit_call.sequence_info = current_transaction.exit_call_counter
                    return current_exit_call
        except Exception as e:
            _logger.error(
                f"Error occurred while starting the exit call: '{e}'.")

    def stop_exit_call(self, exit_call: ExitCall) -> None:
        """
        Stops the exit call.

        Args:
            exit_call: Exit call object
        """

        if not self.has_transaction_started():
            _logger.info("No transaction is active for stop_exit_call().")
        elif isinstance(exit_call, ExitCall) and verify_exit_call(exit_call):
            exit_call.end_time = round(datetime.utcnow().timestamp() * 1000)
            exit_call_event = ExitCallEvent(exit_call.bt_id, exit_call.transaction_guid, exit_call.start_time,
                                            exit_call.end_time, 'REGISTERED', exit_call.backend_id,
                                            self.get_current_transaction().caller_chain, DEFAULT_AGENT_VERSION)

            _logger.debug(
                f"Adding exit call event to be reported: '{exit_call_event}.'")
            self.event_service.add_event(exit_call_event)
        elif exit_call is None:
            _logger.info("Exit call provided for stop_exit_call() was None.")
        else:
            _logger.warning(
                "stop_exit_call() requires a valid instance of ExitCall as the parameter.")

    def get_correlation_header(self, exit_call):
        """
        Return the correlation header string for the provided exit call.

        Args:
          exit_call: Exit call object
        """
        if not isinstance(self.get_current_transaction(), Transaction):
            _logger.info(
                "No valid transaction. Will not create correation header and return None.")
        elif not isinstance(exit_call, ExitCall):
            _logger.warning(
                f"get_correlation_header() requires an instance of ExitCall as the parameter. {exit_call} is not ExitCall instance")
        else:
            corr_header = CorrelationHeader(self.agent_config_response)
            corr_header.generate_sub_headers(
                self.get_current_transaction(), exit_call)
            return str(corr_header)

    def report_error(self, error_name: str, error_message: str) -> None:
        if not error_name:
            _logger.error(
                "Provided error_name is None. Will not report error.")
        elif self.has_transaction_started():
            error_event = ErrorEvent(
                self.current_transaction, error_name, error_message)
            _logger.debug(
                f"Adding error event to be reported: '{error_event}'.")
            self.event_service.add_event(error_event)
        else:
            _logger.debug(
                "Transaction has not started. Will not send error event.")

    def report_exit_call_error(self, error_name: str, error_message: str, exit_call: ExitCall,
                               http_status_code: int = 0) -> None:
        if not error_name:
            _logger.error(
                "Provided error_name is None. Will not report exit call error.")
        elif not self.has_transaction_started():
            _logger.debug(
                "Transaction has not started. Will not send exit call error event.")
        elif not isinstance(exit_call, ExitCall) or not verify_exit_call(exit_call):
            _logger.error(
                "Provided exit call is not a valid ExitCall object. Will not send exit call error event.")
        else:
            error_event = ErrorEvent(self.current_transaction, error_name, error_message,
                                     backend_id=exit_call.backend_id,
                                     http_status_code=http_status_code)

            _logger.debug(
                f"Adding exit call error event to be reported: '{error_event}'.")
            self.event_service.add_event(error_event)

    def cleanup_event_loop(self) -> None:
        """ Clean up all pending futures and tasks in the alternate thread's event_loop on shutdown. """
        if self._thread and self._thread.is_alive():
            for fut in self._concurrent_futures:
                # Only works with `concurrent.Future`. See above comment in Profiler._concurrent_futures.
                try:
                    fut.result()
                except Exception as e:
                    _logger.warning(f"Raised task exception in event loop: {e}")

            # Ensure the lock on agent config
            self.agent_config.stop_lock.acquire(blocking=True, timeout=10)
            tasks = [t for t in asyncio.all_tasks(
                loop=self._event_loop) if t is not asyncio.current_task(self._event_loop) and not t.done()]

            [task.cancel() for task in tasks]

            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
            self._thread.join()
            if self.agent_config.stop_lock.locked():
                self.agent_config.stop_lock.release()

        else:
            _logger.debug("No cleanup required. Thread is not alive.")

    def get_eum_metadata(self, transaction: Transaction) -> Union[dict, None]:
        """
        Returns the eum metadata assuming that the call is an ajax call
        
        Args:
            transaction: Instance of Transaction class

        Returns:
            String containing eum metadata, or none if there is a failure.
        """
        if not transaction or not isinstance(transaction, Transaction):
            _logger.debug("Cannot get the eum metadata as transaction is missing.")
            return

        eum_metadata = None
        headers_container = {}
        try:
            eum_cookie = self.eum.new_eum_cookie(transaction, None, headers_container)
            eum_cookie.set_ajax_call(True)
            eum_cookie.build()
            eum_metadata = headers_container.get("headers")
        except Exception as exception:
            _logger.debug("EUM instance has encountered the following error:")
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.exception(exception)
        
        if eum_metadata is None:
            _logger.debug("Returned eum metadata is None.")

        return eum_metadata


class NoOpProfiler:
    """
    NoOpProfiler will act as a stub when the Profiler object cannot initialize properly and used on startup in the
    SDK approach.
    """

    def start_bt(self, event: Any, context: Any) -> None:
        _logger.debug(
            f"NoOpTracer: Start call issued with event: '{event}' and context: '{context}'.")

    def stop_bt(self) -> None:
        _logger.debug("NoOpTracer: Stop call issued.")

    def report_error(self, error_name: str, error_message: str) -> None:
        _logger.debug(
            f"NoOpTracer: Error '{error_name}' reporting called with message: '{error_message}'.")

    def report_exit_call_error(self, error_name: str, error_message: str, exit_call: ExitCall,
                               http_status_code: int = 0) -> None:
        _logger.debug(f"NoOpTracer: Error '{error_name}' reporting called with message: '{error_message}', with "
                      f"exit_call: '{exit_call}' and status code: '{http_status_code}'.")

    # Stubbed methods for the SDK approach.
    def get_current_transaction(self) -> None:
        _logger.debug("NoOpTracer: No transaction to get.")

    def start_exit_call(self, exit_point_type: str, exit_point_sub_type: str, identifying_properties: dict) -> None:
        _logger.debug(f"NoOpTracer: Received start exit call with: '{exit_point_type}', exit point subtype: "
                      f"'{exit_point_sub_type}', and identifying properties: '{identifying_properties}'.")

    def stop_exit_call(self, exit_call: ExitCall) -> None:
        _logger.debug(
            f"NoOpTracer: Received end exit call with exit call: '{exit_call}'.")

    def get_eum_metadata(self, transaction: Transaction) -> None:
        _logger.debug(
            "NoOpTracer: Get eum metadata call issued")
    
    def get_eum_instance(self) -> None:
        _logger.debug(
            "NoOpTracer: Get eum instance call issued")