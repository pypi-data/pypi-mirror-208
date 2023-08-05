from appdynamics.interceptor.base import ExitCallInterceptor


class BotoHeaderInterceptor(ExitCallInterceptor):
    """
    Boto resource and the classes it spawns do not use _make_request() (except on unsuccessful requests,
    see note below). Method patches _convert_to_request_dict() here:
    https://github.com/boto/botocore/blob/e0fc11c3785437368435a59c41021c0bcb86275f/botocore/client.py#L651

    Method attached is a helper function that returns a dictionary of headers used in the subsequent request. The class
    calling it, _make_api_call()'s parameters do not affect that header output so the helper function existing for
    the boto client to attach to is convienent. If the code changes in a different version, an entirely new approach
    to injecting headers would be required.

    * Note: Even if _make_request() called, the patched method still uses headers monkey patched here.
    """
    def wrap_headers_dedupe(self, func, *args, **kwargs):
        request_dict = func(*args, **kwargs)
        if not isinstance(request_dict, dict):
            self.logger.warning("_convert_request_to_dict method did not return a dictionary.")
        elif "headers" in request_dict:
            request_dict["headers"]['appdIgnore'] = 'True'
        else:
            request_dict["headers"] = {'appdIgnore': 'True'}
        return request_dict


# Attach BotoHeaderInterceptor to _convert_to_request_dict(). See comment above for more details.
def handle_dupe_http_request_exit_calls(profiler, resource):
    # Check attribute chain exists (resource.meta.client._convert_to_request_dict).
    if (hasattr(resource, 'meta') and hasattr(resource.meta, 'client')
            and hasattr(resource.meta.client, '_convert_to_request_dict')):
        interceptor = BotoHeaderInterceptor(profiler, type(resource.meta.client))
        interceptor.attach('_convert_to_request_dict', patched_method_name='wrap_headers_dedupe')
