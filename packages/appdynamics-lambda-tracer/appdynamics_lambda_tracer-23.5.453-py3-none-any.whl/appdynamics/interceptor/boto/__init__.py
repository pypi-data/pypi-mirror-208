from appdynamics.interceptor.boto.boto_interceptor import BotoInterceptor


def intercept_boto(profiler, mod):
    BotoInterceptor(profiler, mod).attach('client', patched_method_name='get_intercepted_boto_client')
    BotoInterceptor(profiler, mod).attach('resource', patched_method_name='get_intercepted_boto_resource')
    BotoInterceptor(profiler, mod).attach('_get_default_session', patched_method_name='patch_session_resource_factory')
