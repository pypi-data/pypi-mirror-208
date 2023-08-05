# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Definition of base entry and exit point interceptors.

"""

from __future__ import unicode_literals
import logging
from functools import wraps
from contextlib import contextmanager
from appdynamics.core.profiler import Profiler, init
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY


class BaseInterceptor(object):
    def __init__(self, profiler, cls):
        self.profiler = profiler
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
        self.cls = cls

    @staticmethod
    def _fix_dunder_method_name(method, class_name):
        # If `method` starts with '__', then it will have been renamed by the lexer to '_SomeClass__some_method'
        # (unless the method name ends with '__').
        if method.startswith('__') and not method.endswith('__'):
            method = '_' + class_name + method
        return method

    def _attach(self, method, wrapper_func, patched_method_name):
        patched_method_name = patched_method_name or '_' + method

        # Deal with reserved identifiers.
        # https://docs.python.org/2/reference/lexical_analysis.html#reserved-classes-of-identifiers
        method = self._fix_dunder_method_name(method, self.cls.__name__)
        patched_method_name = self._fix_dunder_method_name(
            patched_method_name, self.__class__.__name__)

        # Wrap the original method if required.
        original_method = getattr(self.cls, method)

        # Do not intercept the same method more than once.
        if hasattr(original_method, '_appd_intercepted'):
            return
        if wrapper_func:
            @wraps(original_method)
            def wrapped_method(*args, **kwargs):
                return wrapper_func(original_method, *args, **kwargs)
            real_method = wrapped_method
        else:
            real_method = original_method

        # Replace `self.cls.method` with a call to the patched method.
        patched_method = getattr(self, patched_method_name)

        @wraps(original_method)
        def call_patched_method(*args, **kwargs):
            return patched_method(real_method, *args, **kwargs)
        call_patched_method._appd_intercepted = True

        setattr(self.cls, method, call_patched_method)

    def attach(self, method_or_methods, wrapper_func=None, patched_method_name=None):
        if not isinstance(method_or_methods, list):
            method_or_methods = [method_or_methods]
        for method in method_or_methods:
            self._attach(method, wrapper_func, patched_method_name)

    def log_exception(self, exception):
        self.logger.error(exception)

    @contextmanager
    def log_exceptions(self):
        try:
            yield
        except Exception as exception:
            self.log_exception(exception)


NO_WRAPPER = object()


class ExitCallInterceptor(BaseInterceptor):
    def attach(self, method_or_methods, wrapper_func=NO_WRAPPER, patched_method_name=None):
        if method_or_methods:
            if wrapper_func is NO_WRAPPER:
                wrapper_func = self.run
            super(ExitCallInterceptor, self).attach(method_or_methods, wrapper_func=wrapper_func,
                                                    patched_method_name=patched_method_name)
        else:
            self.logger.debug("No methods provided for attachment.")

    def make_correlation_header(self, exit_call):
        if not isinstance(self.profiler, Profiler):
            self.profiler = init()
        header = self.profiler.get_correlation_header(exit_call)
        if header:
            return APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY, header
        return None

    def start_exit_call(self, exit_type, exit_subtype, identifying_props, operation=None, params=None):
        """Start an exit call.
        """
        if not isinstance(self.profiler, Profiler):
            self.profiler = init()
        return self.profiler.start_exit_call(exit_type, exit_subtype, identifying_props)

    def run(self, func, *args, **kwargs):
        """Run the function.  If it raises an exception, end the exit call started from func
           and raise the exception.

           The exit call that needs to be managed should be passed as key word argument appd_exit_call.

        """
        exit_call = kwargs.pop('appd_exit_call', None)
        with self.end_exit_call_and_reraise_on_exception(exit_call):
            return func(*args, **kwargs)

    def end_exit_call(self, exit_call):
        """End the exit call.

        """
        if not isinstance(self.profiler, Profiler):
            self.profiler = init()
        self.profiler.stop_exit_call(exit_call)

    def report_exit_call_error(self, error_name, exit_call, error_message="", http_status_code=0):
        """Reports error for the exit call.
        """
        if not isinstance(self.profiler, Profiler):
            self.profiler = init()
        self.profiler.report_exit_call_error(
            error_name, error_message, exit_call, http_status_code)

    @contextmanager
    def end_exit_call_and_reraise_on_exception(self, exit_call, ignored_exceptions=()):
        try:
            yield
        except ignored_exceptions:
            raise
        except Exception as e:
            self.report_exit_call_error(
                e.__class__.__name__, exit_call, error_message=str(e))

            self.end_exit_call(exit_call)
            raise
