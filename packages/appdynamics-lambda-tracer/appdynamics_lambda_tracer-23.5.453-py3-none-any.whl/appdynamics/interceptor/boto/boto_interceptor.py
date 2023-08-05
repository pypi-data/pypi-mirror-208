from appdynamics.interceptor.base import ExitCallInterceptor
from appdynamics.interceptor.boto.boto_resource_factory_interceptor import BotoResourceFactoryInterceptor
from appdynamics.interceptor.boto.boto_service_interceptor import BotoServiceInterceptor
from appdynamics.interceptor.boto.boto_service_interceptors.aws_lambda_interceptor import LambdaInterceptor
from appdynamics.interceptor.boto.boto_utils.boto_covered_methods import SERVICES_COVERED_MAP
from appdynamics.interceptor.boto.boto_utils.boto_header_interceptor import handle_dupe_http_request_exit_calls


class BotoInterceptor(ExitCallInterceptor):
    """
    BotoInterceptor intercepts calls onto Boto (e.g. boto.client('service')) and returns the client.
    """

    def get_intercepted_boto_client(self, func, *args, **kwargs):
        client = func(*args, **kwargs)
        aws_service = args[0]
        interceptor = services_covered = None
        if aws_service == 'lambda':
            services_covered = SERVICES_COVERED_MAP.get(aws_service)
            interceptor = LambdaInterceptor(self.profiler, type(client), aws_service, services_covered)
        elif aws_service == 'dynamodb':
            services_covered = SERVICES_COVERED_MAP.get(aws_service)
            interceptor = BotoServiceInterceptor(self.profiler, type(client), aws_service, services_covered)
        else:
            self.logger.debug(f"Custom interceptor for boto client: '{aws_service}' is not currently supported.")

        # All boto interceptors use HTTP requests to send requests to services. To avoid double tracking services,
        # attach following method to add header that disables request tracking.
        if interceptor:
            self.logger.debug(f"Attaching interceptor to {aws_service} boto client.")
            interceptor.attach(services_covered, patched_method_name='handle_interception')
            interceptor.attach('_make_request', patched_method_name='dedupe_boto_requests')

        return client

    def get_intercepted_boto_resource(self, func, *args, **kwargs):
        """
        Method used to patch resource factory's  '_convert_to_request_dict()' method. See boto_header_interceptor.py
        for more details.
        """
        resource = func(*args, **kwargs)
        handle_dupe_http_request_exit_calls(self.profiler, resource)
        return resource

    def patch_session_resource_factory(self, func, *args, **kwargs):
        """
        Upon a resource being created, on the first invocation boto3.resource() will call _get_default_session() to
        generate a Session object to be used in all future resources:
        https://github.com/boto/boto3/blob/5485b2c448d0c3403a64bfc1a666149d6db13843/boto3/__init__.py#L27

        Upon instantiation, the Session object will generate a resource_factory object which will be used for creating
        all future resource objects:
        https://github.com/boto/boto3/blob/5485b2c448d0c3403a64bfc1a666149d6db13843/boto3/session.py#L78

        The current approach to patching resources resolves around intercepting the AWS endpoint calls made from
        resource object's implicit do_action() methods that are dynamically created at runtime (see
        boto_resource_factory_interceptor.py for more details). Since the factory object is only created once because
        all sessions are shared, patch that factory._create_action() here to return a wrapped do_action() method.
        """
        session = func(*args, **kwargs)
        if hasattr(session, "resource_factory") and hasattr(session.resource_factory, "_create_action"):
            resource_factory = session.resource_factory
            interceptor = BotoResourceFactoryInterceptor(self.profiler, type(resource_factory), None, [])
            interceptor.attach('_create_action', patched_method_name="handle_interception")
        return session

