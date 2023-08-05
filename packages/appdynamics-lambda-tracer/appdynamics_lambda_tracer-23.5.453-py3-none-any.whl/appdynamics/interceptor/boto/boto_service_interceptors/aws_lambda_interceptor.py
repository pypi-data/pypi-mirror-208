import json
from appdynamics.interceptor.boto.boto_service_interceptor import BotoServiceInterceptor


class LambdaInterceptor(BotoServiceInterceptor):
    """
    Subclass of BotoServiceInterceptor.

    This subclass handles the correlation header and the lambda status codes/errors in response.
    """

    # Overrides BotoServiceInterceptor.update_correlation_header().
    def update_correlation_header(self, current_exit_call, kwargs):
        if not current_exit_call:
            self.logger.debug(
                "Exit call has not yet started. Skipping to update the function payload with the correlation header.")
            return

        # Add correlation header to the lambda payload
        correlation_header = self.make_correlation_header(current_exit_call)
        if correlation_header:
            try:
                # make_correlation_header() returns a tuple of the header key and value
                header = correlation_header[0]
                value = correlation_header[1]
                if header and value:
                    self.logger.debug(
                        f"Adding correlation header to the lambda's invoke API payload - {header}: {value}")

                    # Check if its an asynchronous lambda invoke using lambda_client.invoke_async()
                    invoke_args_json = kwargs.get('InvokeArgs')
                    if invoke_args_json:
                        invoke_args = json.loads(invoke_args_json)
                        invoke_args[header] = value
                        invoke_args_json = json.dumps(invoke_args)
                        kwargs['InvokeArgs'] = invoke_args_json
                        return

                    # Check if the lambda is invoked using lambda_client.invoke() API
                    function_payload_json = kwargs.get('Payload')
                    if function_payload_json:
                        function_payload = json.loads(function_payload_json)
                        function_payload[header] = value

                    # If the payload/event object to the lambda invoke API is empty, then create the payload object.
                    else:
                        function_payload = {header: value}
                    function_payload_json = json.dumps(function_payload)
                    kwargs['Payload'] = function_payload_json
                else:
                    self.logger.debug("No header or no value present. Will not update correlation header.")
            except Exception as e:
                # do nothing
                self.logger.debug(
                    f'Error in updating the function arguments with the correlation header: {e}')
        else:
            self.logger.debug("No correlation header present. Will not update.")

    # Overrides BotoServiceInterceptor.handle_response().
    def handle_response(self, exit_call, response):
        if not exit_call or not response:
            self.logger.debug("No exit call or response to handle.")
            return

        response_metadata = response.get("ResponseMetadata")
        if not response_metadata or not response_metadata.get("HTTPStatusCode"):
            self.logger.debug("ResponseMetadata or HTTPStatusCode field could not be found in boto response.")
            return

        http_status_code = response_metadata.get("HTTPStatusCode")
        function_error = response.get('FunctionError')
        if http_status_code not in [200, 202, 204] or function_error:
            error_message = error_name = 'LAMBDA ERROR'
            if response:
                """
                Boto3 lambda's invoke API response syntax:
                {
                    'StatusCode': 123,
                    'FunctionError': 'string',
                    'LogResult': 'string',
                    'Payload': StreamingBody(),
                    'ExecutedVersion': 'string'
                }
                """
                response_payload_stream = response.get('Payload')
                if response_payload_stream:
                    try:
                        response_payload_json = response_payload_stream.read().decode('utf-8')
                        response_payload = json.loads(response_payload_json)
                        error_message = response_payload.get(
                            'errorMessage', error_message)
                        error_name = response_payload.get('errorType', error_name)
                    except Exception as e:
                        # Do nothing
                        self.logger.debug(f'Error occurred in parsing the function error details: {e}')

            function_error_details = {
                'message': error_message,
                'name': error_name
            }
            self.report_exit_call_error(
                function_error_details['name'], exit_call, error_message=function_error_details['message'],
                http_status_code=http_status_code)
        else:
            self.logger.debug("Successful response.")

    # Overrides BotoServiceInterceptor.get_error_details().
    def get_error_details(self, error):
        error_message = str(error)
        error_name = error.__class__.__name__
        http_status_code = 0  # Default http status code
        # If the exception thrown is a lambda invoke exception, then extract the HTTPStatusCode
        if hasattr(error, 'response'):
            """
            Structure of the botocore clienterror:
            e.response = {
                'Error': {
                    'Message': 'Function not found: arn:aws:lambda:us-west-1:716333212585:function:dprTestLambda123',
                    'Code': 'ResourceNotFoundException'
                }, 'ResponseMetadata': {
                    'RequestId': '7b702fad-aaa7-4fd4-bfe6-b64764260b25',
                    'HTTPStatusCode': 404,
                    'HTTPHeaders': {'date': 'Wed, 22 Jan 2020 22:45:07 GMT', 'content-type': 'application/json', 
                                    'content-length': '111', 'connection': 'keep-alive', 
                                    'x-amzn-requestid': '7b702fad-aaa7-4fd4-bfe6-b64764260b25', 
                                    'x-amzn-errortype': 'ResourceNotFoundException'
                                    },
                    'RetryAttempts': 0
                }
            }
            """
            error_response_metadata = error.response.get('ResponseMetadata')
            if error_response_metadata:
                http_status_code = error_response_metadata.get('HTTPStatusCode', http_status_code)

        return {
            'message': error_message,
            'name': error_name,
            'http_status_code': http_status_code
        }
