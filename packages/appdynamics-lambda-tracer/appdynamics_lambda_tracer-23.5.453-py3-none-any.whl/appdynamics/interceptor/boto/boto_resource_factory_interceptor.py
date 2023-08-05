from appdynamics.interceptor.boto.boto_service_interceptor import BotoServiceInterceptor


class BotoResourceFactoryInterceptor(BotoServiceInterceptor):
    """
    BotoResourceFactoryInterceptor serves to patch the action method created by the Boto3 resource factory here:
    https://github.com/boto/boto3/blob/5485b2c448d0c3403a64bfc1a666149d6db13843/boto3/resources/factory.py#L485

    Resource class created here:
    https://github.com/boto/boto3/blob/5485b2c448d0c3403a64bfc1a666149d6db13843/boto3/resources/factory.py#L139

    This action method is generated and returned based on the JSON files that dynamically generate the resource classes.
    The method is fed into the class created at runtime and uses the built-in property() method to build in the
    getters for the methods and cannot be altered after created (without subclassing). The handle_interception() method
    below, wraps the action method returned to create and close exit calls and bake that into the returned action.

    Worth noting is the difference between the outer `interceptor_self` and the inner action_wrapper `self`. The two
    are different where the `interceptor_self` represents the AppD interceptor class while the `self` represents the
    dynamically generated classes' self (i.e. the resource). The distinction is important as conflating the two in
    the wrapper would cause the resource to not have the proper class reference when sending the request to the
    AWS endpoint.
    """
    def handle_interception(interceptor_self, func, *interceptor_args, **interceptor_kwargs):
        do_action_func = func(*interceptor_args, **interceptor_kwargs)

        def action_wrapper(self, *args, **kwargs):
            exit_call = aws_service_name = None
            if hasattr(self, "__class__"):
                aws_service_name = self.__class__.__name__.split('.')[0]
                exit_call = interceptor_self.create_exit_call(args, kwargs, aws_service_name=aws_service_name,
                                                              aws_resource_class=self)
            try:
                return do_action_func(self, *args, **kwargs)
            except Exception as e:
                if exit_call:
                    error_details = interceptor_self.get_error_details(e)
                    interceptor_self.report_exit_call_error(error_details.get('name', f"{aws_service_name}_error"),
                                                            exit_call,
                                                            http_status_code=error_details.get('http_status_code', 0),
                                                            error_message=error_details.get('message',
                                                                                            f"{aws_service_name}_error")
                                                            )
                raise
            finally:
                if exit_call:
                    interceptor_self.logger.debug("Stopping the exit call to lambda.")
                    interceptor_self.end_exit_call(exit_call)

        return action_wrapper
