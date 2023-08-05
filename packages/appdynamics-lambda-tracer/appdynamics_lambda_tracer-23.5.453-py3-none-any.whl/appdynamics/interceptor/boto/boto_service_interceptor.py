from appdynamics.interceptor.base import ExitCallInterceptor
from appdynamics.interceptor.boto.boto_utils.boto_backend_properties import get_backend_properties


class BotoServiceInterceptor(ExitCallInterceptor):
    """
    Generalized interceptor designed for extensibility if more boto client interceptors are required in the future. This
    class is designed around the fact that all client interceptors will follow the same exit call pattern: create exit
    call, update correlation header if needed, call original function, handle response if needed, catch & report any
    errors, and close the exit call.

    Future boto client interceptors will can use this class if error handling is generic and there is no need to update
    the correlation header and no need to handle the response.
    """

    def __init__(self, profiler, cls, aws_service_name, services_covered):
        super().__init__(profiler, cls)
        self.aws_service_name = aws_service_name
        # services_covered constants have the format "Word1_Word2". Operational model name expects the format
        # "Word1Word2".
        self.services_covered = [item.replace("_", "") for item in services_covered]

    """
    Main interceptor method. All boto interceptors will have the same code flow but may vary based on which methods
    they decide to override.
    """
    def handle_interception(self, func, *args, **kwargs):
        exit_call = self.create_exit_call(args, kwargs)
        try:
            # Not all tracked methods require correlation header to updated.
            self.update_correlation_header(exit_call, kwargs)
            response = func(*args, **kwargs)
            # Not all tracked methods have require response handling.
            self.handle_response(exit_call, response)
            return response
        except Exception as e:
            if exit_call:
                error_details = self.get_error_details(e)
                self.report_exit_call_error(error_details.get('name', f"{self.aws_service_name}_error"),
                                            exit_call,
                                            http_status_code=error_details.get('http_status_code', 0),
                                            error_message=error_details.get('message',
                                                                            f"{self.aws_service_name}_error"))
                self.logger.debug("Stopping the exit call to lambda")
            raise
        finally:
            if exit_call:
                self.end_exit_call(exit_call)

    """
    Helper function for handle_interception() to fetch backend properties and handle exit call creation.
    """
    def create_exit_call(self, args, kwargs, aws_service_name=None, aws_resource_class=None):
        service_name = aws_service_name if aws_service_name else self.aws_service_name
        backend_prop = get_backend_properties(service_name, aws_resource_class, args, kwargs)
        if backend_prop:
            self.logger.debug(
                f"Starting an exit call with exit_type = ${backend_prop['exit_type']} exit_sub_type = "
                f"${backend_prop['exit_sub_type']} and identifying_properties = "
                f"${backend_prop['identifying_properties']}")

            return self.start_exit_call(backend_prop['exit_type'], backend_prop['exit_sub_type'],
                                        backend_prop['identifying_properties'])
        else:
            self.logger.warning(f"No backend properties found for name {self.aws_service_name}. No exit call started.")

    """
    Correlation headers only need to be updated for specific clients (e.g. lambdas, SNS, SQS). May be overridden in 
    subclasses that need to update the correlation header.
    """
    def update_correlation_header(self, exit_call, kwargs):
        self.logger.debug("update_correlation_header() called but nothing to do.")

    """
    Checks the http status code. May be overridden in subclasses that require further response handling.
    """
    def handle_response(self, exit_call, response):
        if not exit_call or not response:
            self.logger.debug("No exit call or response to handle.")
            return

        # Every boto response has ResponseMetadata field past version 0.6.4 and every ResponseMetadata since 0.7.0 has
        # 'HTTPStatusCode' field. Check in case using a very deprecated boto version (2/13/2013).
        response_metadata = response.get("ResponseMetadata")
        if not response_metadata or not response_metadata.get("HTTPStatusCode"):
            self.logger.debug("ResponseMetadata or HTTPStatusCode field could not be found in boto response.")
            return

        http_status_code = response_metadata.get("HTTPStatusCode")
        if http_status_code not in [200, 202, 204]:
            error_message = error_name = f"{self.aws_service_name} Non-200 HTTP response"
            self.report_exit_call_error(error_name, exit_call,
                                        error_message=error_message,
                                        http_status_code=http_status_code)

    """
    Simple error handler. May be overridden in subclasses that require error handling.
    """
    def get_error_details(self, error):
        return {
            'message': str(error),
            'name': error.__class__.__name__,
            'http_status_code': 0  # Default http status code
        }

    """
    BotoCore calls _make_request() (see link below) right before issuing an HTTP request to the AWS service endpoint. 
    This interceptor checks the request to see if it matches our tracked methods and if it does, add header to ignore 
    HTTP exit call. This allows to avoid duplicating exit calls.
    https://github.com/boto/botocore/blob/e0fc11c3785437368435a59c41021c0bcb86275f/botocore/client.py#L639
    """
    def dedupe_boto_requests(self, func, *args, **kwargs):
        self.logger.debug(f"Handling outgoing boto HTTP requests to AWS for {self.aws_service_name}.")
        request_args = list(args)
        # Args is a tuple. So we need to convert it to a list before updating
        if len(request_args) >= 3:
            operation_model = request_args[1]
            operation_model_name = getattr(operation_model, 'name', None)
            if isinstance(operation_model_name, str) and operation_model_name.lower() in self.services_covered:
                if 'headers' in request_args[2]:
                    request_args[2]['headers']['appdIgnore'] = 'True'
                else:
                    request_args[2]['headers'] = {'appdIgnore': 'True'}
            else:
                self.logger.debug(f"Service {operation_model_name} is not covered. Will not add appdIgnore header.")

        return func(*tuple(request_args), **kwargs)
