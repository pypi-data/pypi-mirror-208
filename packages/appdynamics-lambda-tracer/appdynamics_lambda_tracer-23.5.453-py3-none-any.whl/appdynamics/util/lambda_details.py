import os

from appdynamics.util.constants import APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY


class LambdaDetails:
    def __init__(self):
        self._function_name = os.getenv(
            "AWS_LAMBDA_FUNCTION_NAME", "test_function_name")
        self._function_version = os.getenv(
            "AWS_LAMBDA_FUNCTION_VERSION", "test_function_version")

    @property
    def function_name(self):
        return self._function_name

    @function_name.setter
    def function_name(self, function_name):
        self._function_name = function_name

    @property
    def function_version(self):
        return self._function_version

    @function_version.setter
    def function_version(self, function_version):
        self._function_version = function_version

    """
      Fetch the correlation header from the following places in order:
      1.) context.client_context.env => context.client_context.env[constants.APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY] https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
      2.) event => event[constants.APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY] https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html
      3.) event.headers => event.headers[constants.APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY] https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html
    """

    def get_correlation_header_value(self, lambda_event, lambda_context):
        if lambda_context and lambda_context.client_context and lambda_context.client_context.env and lambda_context.client_context.env.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY):
            return lambda_context.client_context.env.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY)
        if lambda_event and isinstance(lambda_event, dict) and lambda_event.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY):
            return lambda_event.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY)
        if lambda_event and isinstance(lambda_event, dict) and lambda_event.get("headers"):
            lambda_event_headers = lambda_event.get("headers")
            if isinstance(lambda_event_headers, dict) and lambda_event_headers.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY):
                return lambda_event_headers.get(APPDYNAMICS_TRANSACTION_CORRELATION_HEADER_KEY)
