from importlib.machinery import ModuleSpec
from appdynamics.interceptor import http, boto
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME
import logging
import importlib
import sys

EXIT_CALL_INTERCEPTORS = (
    # HTTP exit calls
    ('httplib', http.intercept_httplib),
    ('http.client', http.intercept_httplib),
    ('urllib3', http.intercept_urllib3),
    ('requests', http.intercept_requests),
    ('boto.https_connection', http.intercept_boto),
    ('tornado.httpclient', http.intercept_tornado_httpclient),
    ('boto3', boto.intercept_boto)
)


def bootstrap_interceptors(profiler):
    hook = add_hook(profiler)
    for mod, patch in EXIT_CALL_INTERCEPTORS:
         hook.call_on_import(mod, patch)


def add_hook(profiler):
    """Add the module interceptor hook for AppDynamics, if it's not already registered.

    """

    interceptor = ModuleInterceptor(profiler)
    sys.meta_path.insert(0, interceptor)
    return interceptor


class ModuleInterceptor(object):
    """Intercepts finding and loading modules in order to monkey patch them on load.
      Acts as both python's meta path finder https://docs.python.org/3.8/library/importlib.html#importlib.abc.MetaPathFinder
      as well as python module loader https://docs.python.org/3.8/library/importlib.html#importlib.abc.Loader
    """

    def __init__(self, profiler):
        super(ModuleInterceptor, self).__init__()
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
        self.profiler = profiler
        self.module_hooks = {}
        self.intercepted_modules = set()

    def find_spec(self, full_name, path, target=None):
        if full_name in self.module_hooks:
            return ModuleSpec(full_name, self)
        return None

    def find_module(self, full_name, path=None):
        if full_name in self.module_hooks:
            return self
        return None

    def load_module(self, name):
        # Remove the module from the list of hooks so that we never see it again.
        hooks = self.module_hooks.pop(name, [])

        if name in sys.modules:
            # Already been loaded. Return it as is.
            return sys.modules[name]

        self.logger.debug(f"Intercepting import {name}")

        # __import__('a.b.c') returns <module a>, not <module a.b.c>
        __import__(name)
        module = sys.modules[name]  # ...so get <module a.b.c> from sys.modules

        self._intercept_module(module, hooks)
        return module

    def call_on_import(self, module_name, cb):
        if module_name in sys.modules:
            self._intercept_module(sys.modules[module_name], [cb])
        else:
            self.module_hooks.setdefault(module_name, [])
            self.module_hooks[module_name].append(cb)

    def _intercept_module(self, module, hooks):
        try:
            for hook in hooks:
                self.logger.debug(f"Running {module.__name__} hook {hook}")
                hook(self.profiler, module)
            self.intercepted_modules.add(module)
        except:
            self.logger.error(f"Exception in {module.__name__} hook.")

            # Re-import to ensure the module hasn't been partially patched.
            self.logger.debug(
                f"Re-importing {module.__name__} after error in module hook")
            importlib.reload(module)
