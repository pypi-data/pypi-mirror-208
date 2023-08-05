from __future__ import unicode_literals
import functools
import inspect
from appdynamics.interceptor.http import HTTPConnectionInterceptor
from urllib.parse import urlparse

try:
    import tornado.httpclient

    class AsyncHTTPClientInterceptor(HTTPConnectionInterceptor):
        def start_exit_call(self, url):
            exit_call = None
            parsed_url = urlparse(url)
            port = parsed_url.port or (
                '443' if parsed_url.scheme == 'https' else '80')
            host = parsed_url.hostname
            if port and host:
                backend_identifying_props = self.get_identifying_properties(
                    host, port)
                exit_call = super(AsyncHTTPClientInterceptor, self).start_exit_call(
                    "HTTP", "HTTP", backend_identifying_props)
            return exit_call

        def end_exit_call(self, exit_call, *args, **kwargs):
            response = None
            response_future = args[0]
            if response_future.done() and not response_future.cancelled():
                if response_future.exception():
                    response_exception = response_future.exception()
                    http_code = getattr(response_exception, 'code', 0)
                    self.report_exit_call_error(
                        str(response_exception), exit_call, http_status_code=http_code)
                else:
                    response = response_future.result()

            if response:
                response_status_code = response.code
                url = response.request.url
                parsed_url = urlparse(url)
                url_port = parsed_url.port or (
                    '443' if parsed_url.scheme == 'https' else '80')
                url_host = parsed_url.hostname
                url_path = parsed_url.path
                self.handle_http_status_code(
                    response_status_code, url_host, url_port, url_path, exit_call)

            super(AsyncHTTPClientInterceptor, self).end_exit_call(exit_call)

        def _fetch(self, fetch, client, request, callback=None, raise_error=True, **kwargs):
            exit_call = None
            with self.log_exceptions():
                is_request_object = isinstance(
                    request, tornado.httpclient.HTTPRequest)
                url = request.url if is_request_object else request
                exit_call = self.start_exit_call(url)
                if exit_call:
                    correlation_header = self.make_correlation_header(
                        exit_call)
                    if correlation_header:
                        headers = request.headers if is_request_object else kwargs.setdefault(
                            'headers', {})
                        headers[correlation_header[0]] = correlation_header[1]

            fetch_parameters = inspect.signature(fetch).parameters
            # Callback flag deprecated in tornado 5.1.
            if 'callback' not in fetch_parameters:
                future = fetch(client, request,
                               raise_error=raise_error, **kwargs)

            # The `raise_error` kwarg was added in tornado 4.1.  Passing it by name on versions
            # prior to this cause it to be included in the `**kwargs` parameter to `fetch`.  This
            # dict is passed directly to the `HTTPRequest` constructor, which does not have
            # `raise_error` in its signature and thus raises a TypeError.
            elif 'raise_error' in fetch_parameters:
                future = fetch(client, request, callback=callback,
                               raise_error=raise_error, **kwargs)
            else:
                future = fetch(client, request, callback=callback, **kwargs)
            future.add_done_callback(
                functools.partial(self.end_exit_call, exit_call))
            return future

    def intercept_tornado_httpclient(profiler, mod):
        # these methods don't normally return anything, but to be able to test that
        # the 'empty' interceptor defined below works properly, return a value here.
        return AsyncHTTPClientInterceptor(profiler, mod.AsyncHTTPClient).attach('fetch', wrapper_func=None)
except ImportError:
    def intercept_tornado_httpclient(agent, mod):
        pass
