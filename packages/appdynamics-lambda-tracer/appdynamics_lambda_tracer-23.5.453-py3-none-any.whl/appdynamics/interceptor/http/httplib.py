"""Interceptor for httplib/http.client.

"""

from __future__ import unicode_literals

from datetime import datetime
from urllib.parse import urlparse
from appdynamics.interceptor.http import HTTPConnectionInterceptor


class HttplibConnectionInterceptor(HTTPConnectionInterceptor):
    def _putrequest(self, putrequest, connection, method, url, *args, **kwargs):
        # We note down the start time here because putrequest() marks the true start time
        # for the http exit call
        connection._appd_exit_call_start_time = round(
            datetime.utcnow().timestamp() * 1000)
        connection._appd_exit_call_full_url = urlparse(url).path
        return putrequest(connection, method, url, *args, **kwargs)

    def _putheader(self, putheader, connection, *args, **kwargs):
        # We need to check for the presence of appdIgnore header in case the http exit call
        # has already been intercepted by another interceptor. For example, the calls to lambda
        # using boto3 api is already intercepted by the lambda interceptor.
        if 'appdIgnore' in args:
            connection._appd_ignore_exit_call = True
        return putheader(connection, *args, **kwargs)

    def _endheaders(self, endheaders, connection, *args, **kwargs):
        exit_call = None
        ignore_exit_call = getattr(connection, '_appd_ignore_exit_call', None)
        if not ignore_exit_call:
            with self.log_exceptions():
                backend_identifying_props = self.get_identifying_properties(
                    connection.host, connection.port)
                exit_call = self.start_exit_call(
                    "HTTP", "HTTP", backend_identifying_props)
                if exit_call:
                    # Override the exit call start time with the actual http call start time
                    # which was noted in putrequest() method.
                    if hasattr(exit_call, 'start_time') and hasattr(connection, '_appd_exit_call_start_time'):
                        exit_call.start_time = connection._appd_exit_call_start_time
                        del connection._appd_exit_call_start_time
                    connection._appd_exit_call = exit_call
                    header = self.make_correlation_header(exit_call)
                    if header is not None:
                        connection.putheader(*header)
                        self.logger.debug(
                            'Added correlation header to HTTP request: %s, %s' % header)
        else:
            del connection._appd_ignore_exit_call

        return endheaders(connection, appd_exit_call=exit_call, *args, **kwargs)

    def _getresponse(self, getresponse, connection, *args, **kwargs):
        # CORE-40945 Catch TypeError as a special case for Python 2.6 and call getresponse with just the
        # HTTPConnection instance.
        exit_call = getattr(connection, '_appd_exit_call', None)
        exit_call_url_path = getattr(
            connection, '_appd_exit_call_full_url', '/')
        response = None
        try:
            with self.end_exit_call_and_reraise_on_exception(exit_call,
                                                             ignored_exceptions=(TypeError,)):
                response = getresponse(connection, *args, **kwargs)
        except TypeError:
            with self.end_exit_call_and_reraise_on_exception(exit_call):
                response = getresponse(connection)

        self.logger.debug(
            f"Response is: {response.status} for host {connection.host}, port {connection.port} and path {exit_call_url_path}")
        response_status_code = response.status
        # Mark exit call as error exit call if http status code falls in error range
        self.handle_http_status_code(
            response_status_code, connection.host, connection.port, exit_call_url_path, exit_call)
        if exit_call:
            self.end_exit_call(exit_call)
        try:
            del connection._appd_exit_call
            del connection._appd_exit_call_full_url
        except AttributeError:
            pass
        return response


def intercept_httplib(profiler, mod):
    HTTPConnectionInterceptor.https_connection_classes.add(mod.HTTPSConnection)
    interceptor = HttplibConnectionInterceptor(profiler, mod.HTTPConnection)
    interceptor.attach(['putrequest', 'endheaders', 'putheader'])
    # CORE-40945 Do not wrap getresponse in the default wrapper.
    interceptor.attach('getresponse', wrapper_func=None)
