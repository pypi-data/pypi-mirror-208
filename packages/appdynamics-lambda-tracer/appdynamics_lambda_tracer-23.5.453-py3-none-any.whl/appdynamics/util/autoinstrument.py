"""
This module is called by autoinstrument-tracer.pth to autoinstrument the customer lambda.
More info on .pth files and code execution can be found here: 
http://blog.dscpl.com.au/2015/04/automatic-patching-of-python.html
It works by wrapping the imp.load_module() call which is used to load the customer lambda
and performing the instrumentation after the customer lambda handler has been imported.
"""
import imp
import os

def wrap_imp_load_module(wrapped):

    def wrapper(*args, **kwargs):
        module = wrapped(*args, **kwargs)

        # NOTE: We don't strip whitespace because the AWS lambda python bootstrap does not do this. In
        # fact you can't set a handler to have whitespace using either AWS Lambda web interface or cli.
        handler = os.environ.get("_HANDLER", "")

        # rsplit(".", 1) only splits by the first delimiter starting from the end, i.e. "a.b.c.d" -> ["a.b.c", "d"]
        split_handler = handler.rsplit(".", 1)

        if len(split_handler) == 2 and args[0] == split_handler[0]:
            print("Intercepted imp.load_module() call, wrapping handler with Appdynamics tracer.")
            import appdynamics
            function_name = split_handler[1]
            # get handler function from module
            function = getattr(module, function_name)
            # set handler function to our wrapped version
            setattr(module, function_name, appdynamics.tracer(function))

        return module

    return wrapper


def autoinstrument():
    # Wrap imp.load_module(), this is the call the lambda runtime uses to load the customer lambda handler.
    # NOTE: The AWS python bootstrap might potentially use a different import mechanism in future versions
    # so this might have to be revisited.
    imp.load_module = wrap_imp_load_module(imp.load_module)
