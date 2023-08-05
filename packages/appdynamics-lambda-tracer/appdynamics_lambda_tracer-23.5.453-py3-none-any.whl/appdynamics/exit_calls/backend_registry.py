import logging

from appdynamics.exit_calls.registered_backend_info import generate_registered_backend_info
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME


class BackendRegistry:
    """BackendRegistry class contains a registry of the registered backends.

     It also contains the associated utility methods to store and fetch the registered backend
     information for a given exit_point_type, exit_point_sub_type & identifying_properties.

    Attributes:
        registry: Dictionary containing the registered backends.
        logger: Reference to the python in-built logger.
    """

    def __init__(self):
        self.registry = {}
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

    def update_registry(self, registered_backends):
        """
        Updates the registry attribute with the registered backends.
        The key and value for the registry are as follows:
            key = exit_point_type, exit_point_sub_type & identifying_properties are passed to a special
                function get_registry_key() to get a unique key.
            value = a `RegisteredBackendInfo` object

        Args:
            registered_backends: Array of registered backend objects. This info is obtained from
            the agent config response.
        """
        if registered_backends and isinstance(registered_backends, list):
            self.logger.debug(
                "Updating the backend registry with the registered backends.")
            self.registry.clear()

            expected_fields = ["exit_point_type", "exit_point_sub_type", "backend_id", "identifying_properties",
                               "resolved_entity_type", "resolved_entity_id"]
            for backend in registered_backends:
                if all(field in backend for field in expected_fields):
                    registry_key = get_registry_key(backend['exit_point_type'], backend['exit_point_sub_type'],
                                                    backend['identifying_properties'])
                    self.registry[registry_key] = generate_registered_backend_info(
                        backend)
            self.logger.debug(f"New backend registry: '{self.registry}'.")
        else:
            self.logger.debug(
                "No registered backends present. Not updating the backend registry.")

    def get_registered_backend_info(self, exit_point_type, exit_point_sub_type, identifying_properties):
        """
        Function to get the registration information of a backend from the registry attribute for a given set of exit
        call properties.
        Returns:
            registered_backend_info: Instance of RegisteredBackendInfo class.
            None: if the backend is not yet registered with the controller.
        """
        if exit_point_type and exit_point_sub_type and identifying_properties:
            self.logger.debug(f"Searching for backend with type = {exit_point_type}, exit point sub type = "
                              f"{exit_point_sub_type} and identifying_properties = {identifying_properties} "
                              f"in the backend registry.")

            registry_key = get_registry_key(
                exit_point_type, exit_point_sub_type, identifying_properties)
            if registry_key in self.registry:
                return self.registry[registry_key]
            self.logger.debug("Backend could not be found.")
        else:
            self.logger.warning("One/more of the required exit call properties (exit_point_type, exit_point_sub_type, "
                                "identifying_properties) are missing. Can't fetch the registered backend info.")


def get_registry_key(exit_point_type, exit_point_sub_type, identifying_properties):
    """
    Function computes a unique key for a given exit call.
    The returned value is used as the key to the registry dictionary.

    Output format is a tuple with fields:
    (exit_pt_type, exit_pt_sub_type,
     ((sorted_prop1, sorted_val1), (sorted_prop2, sorted_val2), ...))
    """

    return exit_point_type, exit_point_sub_type, tuple(sorted(map(lambda d: tuple([d["property"], d["value"]]), identifying_properties)))
