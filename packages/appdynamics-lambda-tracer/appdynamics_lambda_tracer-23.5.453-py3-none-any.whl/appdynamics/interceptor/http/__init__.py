"""Base class for HTTP connection interceptors.

"""

from __future__ import unicode_literals
from appdynamics.interceptor.base import ExitCallInterceptor


class HTTPConnectionInterceptor(ExitCallInterceptor):
    # If the library you are intercepting has an HTTPSConnection class which
    # does not subclass httplib.HTTPSConnection, add it to this set.
    https_connection_classes = set()

    def get_identifying_properties(self, host, port):
        identifying_properties = {
            "HOST": host,
            "PORT": str(port)
        }
        return identifying_properties

    def handle_http_status_code(self, status_code, http_host, http_port, http_path, exit_call):
        if status_code < 200 or status_code >= 400:
            error_msg = f"Error code {status_code} for host {http_host}, port {http_port} and path {http_path}"
            self.report_exit_call_error(
                "HTTP Error", exit_call, http_status_code=status_code, error_message=error_msg)

from appdynamics.interceptor.http.boto import intercept_boto
from appdynamics.interceptor.http.httplib import intercept_httplib
from appdynamics.interceptor.http.requests import intercept_requests
from appdynamics.interceptor.http.tornado_httpclient import intercept_tornado_httpclient
from appdynamics.interceptor.http.urllib3 import intercept_urllib3
__all__ = ['intercept_httplib', 'intercept_urllib3', 'intercept_requests', 'intercept_boto',
           'intercept_tornado_httpclient']
