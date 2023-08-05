import logging

from types import TracebackType
from typing import Any, Union, Optional, Type

from appdynamics.core.profiler import init
from appdynamics.exit_calls.exit_call import ExitCall
from appdynamics.transactions.transaction import Transaction
from appdynamics.util.config import is_tracer_disabled
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME

logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)


def tracer(handler):
    """
    Decorator for AppDynamics Python Tracer.

    Acts as wrapper around customer code where we can initialize our profiler, and call start & stop on the transaction.
    The core logic of code will live inside profiler.py.

        Typical Usage:

        import appdynamics

        @appdynamics.tracer
        def handler(event, context):
            print("Hello world!")

    Args:
        handler: The customer's handler function.

    Returns:
        A wrapped function for the lambda to run.
    """

    def wrapper(*args, **kwargs):
        if is_tracer_disabled():
            global logger
            logger.info("Tracer is disabled. 'APPDYNAMICS_DISABLE_AGENT' is set to true.")
            return handler(*args, **kwargs)

        profiler = init()
        profiler.start_bt(*args)
        transaction = profiler.get_current_transaction()
        ret_val = None
        lambda_event = args[0] if len(args) > 0 else None
        exception_raised = False
        try:
            ret_val = handler(*args, **kwargs)
        except Exception as exception:
            profiler.report_error(type(exception).__name__, str(exception))
            exception_raised = True
            raise
        finally:
            profiler.stop_bt()
            if ret_val is not None:
                #only run EUM if no errors in transaction
                if not exception_raised:
                    eum = profiler.get_eum_instance()
                    if eum is not None:
                        eum.run_eum(transaction, lambda_event, ret_val)
                return ret_val

    return wrapper


# Helper wrapper function to not run methods if 'APPDYNAMICS_DISABLE_AGENT' is true.
def _run_if_tracer_enabled(func):
    def run_or_not(*args, **kwargs):
        if func and hasattr(func, '__name__'):
            if is_tracer_disabled():
                global logger
                logger.debug(f"Tracer is disabled. 'APPDYNAMICS_DISABLE_AGENT' is set to true. "
                             f"Function '{func.__name__}' will not be run.")
            else:
                return func(*args, **kwargs)
    return run_or_not


""" The following methods are exposed for end users to have a fine-grained control over their tracer and/or
the ability to manually create exit calls and errors that may not be picked up in the above wrapper. """


@_run_if_tracer_enabled
def create_transaction(event: Any, context: Any) -> None:
    """
    Initializes the transaction which will start the business transaction and log metrics for the controller.

    :param event: Event passed in from lambda.
    :param context: Context passed in through lambda.
    :return:
    """
    init().start_bt(event, context)


@_run_if_tracer_enabled
def stop_transaction() -> None:
    """
    Stops the active transaction.

    :return:
    """
    init().stop_bt()


@_run_if_tracer_enabled
def get_current_transaction() -> Union[Transaction, None]:
    """
    Returns the active transaction or None if no transaction active.

    :return: Transaction object or None
    """
    return init().get_current_transaction()


@_run_if_tracer_enabled
def start_exit_call(exit_point_type: str, exit_point_sub_type: str, identifying_properties: dict) \
        -> Union[ExitCall, None]:
    """
    Starts a new exit call given exit point type, exit point subtype, and identifying properties. Returns
    the active exit call which should later be passed into stop_exit_call() or report_exit_call_error().

    :param exit_point_type: String
    :param exit_point_sub_type: String
    :param identifying_properties: Dictionary of Strings
    :return: ExitCall object
    """
    return init().start_exit_call(exit_point_type, exit_point_sub_type, identifying_properties)


@_run_if_tracer_enabled
def stop_exit_call(exit_call: ExitCall) -> None:
    """
    Stops the exit call given.

    :param exit_call: ExitCall object
    :return:
    """
    init().stop_exit_call(exit_call)


@_run_if_tracer_enabled
def report_error(error_name: str, error_message: str) -> None:
    """
    Reports an error to the controller.

    :param error_name: String
    :param error_message: String
    :return:
    """
    init().report_error(error_name, error_message)


@_run_if_tracer_enabled
def report_exit_call_error(error_name: str, error_message: str, exit_call:
                           ExitCall, http_status_code: int = 0) -> None:
    """
    Reports an error during an exit call to the controller.
    
    :param error_name: String
    :param error_message: String
    :param exit_call: ExitCall object
    :param http_status_code: optional - int
    :return: 
    """
    init().report_exit_call_error(error_name, error_message, exit_call, http_status_code=http_status_code)


@_run_if_tracer_enabled
def get_eum_metadata(transaction: Transaction) -> Union[dict, None]:
    """
    Returns eum metadata string.

    :param transaction: Transaction
    :return: dict or None
    """
    return init().get_eum_metadata(transaction)


class TransactionContextManager:
    """
    Context manager class for the tracer.
    """
    def __init__(self, event: Any, context: Any):
        if not is_tracer_disabled():
            self.profiler = init()
            self.profiler.start_bt(event, context)

    @_run_if_tracer_enabled
    def __enter__(self):
        return self

    @_run_if_tracer_enabled
    def __exit__(self, exception_type: Optional[Type[BaseException]], exception_value: Optional[BaseException], 
                 traceback: Optional[TracebackType]):
        if exception_type:
            self.profiler.report_error(exception_type.__name__, str(exception_value))
        self.profiler.stop_bt()


class ExitCallContextManager:
    """
    Context manager class for exit calls.
    """
    def __init__(self, exit_point_type: str, exit_point_sub_type: str, identifying_properties: dict):
        if not is_tracer_disabled():
            self.profiler = init()
            self.exit_call = self.profiler.start_exit_call(exit_point_type, exit_point_sub_type, identifying_properties)

    @_run_if_tracer_enabled
    def __enter__(self):
        return self

    @_run_if_tracer_enabled
    def __exit__(self, exception_type: Optional[Type[BaseException]], exception_value: Optional[BaseException], 
                 traceback: Optional[TracebackType]):
        if exception_type:
            self.profiler.report_exit_call_error(exception_type.__name__, str(exception_value), self.exit_call, 0)
        self.profiler.stop_exit_call(self.exit_call)

    @_run_if_tracer_enabled
    def report_exit_call_error(self, error_name: str, error_message: str, 
                               http_status_code: int = 0) -> None:
        self.profiler.report_exit_call_error(error_name, error_message, self.exit_call, http_status_code)