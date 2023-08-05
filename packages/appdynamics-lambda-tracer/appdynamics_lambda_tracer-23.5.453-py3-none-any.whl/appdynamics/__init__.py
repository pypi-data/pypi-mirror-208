from .core.tracer import tracer, create_transaction, stop_transaction, get_current_transaction, start_exit_call, \
    stop_exit_call, report_error, report_exit_call_error, get_eum_metadata, TransactionContextManager, \
    ExitCallContextManager
from .core.profiler import init
from .interceptor import bootstrap_interceptors
from .util.config import is_tracer_disabled

if not is_tracer_disabled():
    profiler = init()
    bootstrap_interceptors(profiler)

