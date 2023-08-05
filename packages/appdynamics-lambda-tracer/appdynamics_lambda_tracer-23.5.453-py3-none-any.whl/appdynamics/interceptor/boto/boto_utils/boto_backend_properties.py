import logging
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME

logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)


def ddb_backend_properties(table_name):
    return {
        "exit_type": "DB",
        "exit_sub_type": "DB",
        "identifying_properties": {
            "DESTINATION_TYPE": "DB",
            "DESTINATION": table_name
        }
    }


def lambda_backend_properties(func_name):
    return {
        "exit_type": "CUSTOM",
        "exit_sub_type": "CUSTOM",
        "identifying_properties": {
            "DESTINATION_TYPE": "LAMBDA",
            "DESTINATION": func_name
        }
    }


BACKEND_PROPERTIES_FUNCTION_MAP = {
    "dynamodb": ddb_backend_properties,
    "lambda": lambda_backend_properties
}


def get_backend_properties(service_name, aws_resource_class, args, kwargs):
    backend_property_function = BACKEND_PROPERTIES_FUNCTION_MAP.get(service_name)
    if backend_property_function:
        return backend_property_function(get_identifier(service_name, aws_resource_class, args, kwargs))
    else:
        logger.warning(f"No service name found called: {service_name}")


def get_identifier(service_name, aws_resource_class, args, kwargs):
    if service_name == "dynamodb":
        # kwargs always will be a dict.
        if kwargs.get("TableName"):
            return kwargs.get("TableName")
        # args is a tuple and the second element is the TableName.
        elif len(args) >= 2 and isinstance(args[1], str):
            return args[1]
        # Table.name field will contain the identifier if passed.
        elif aws_resource_class and hasattr(aws_resource_class, "name"):
            return aws_resource_class.name
    elif service_name == "lambda":
        return kwargs.get('FunctionName')

    logger.warning("No subresource identifier found. Returning 'default' as identifying property.")
    # Bug in libagent where if DESTINATION field is left null, no backend will show up and will silently fail.
    # Always return a string here.
    return "default"
