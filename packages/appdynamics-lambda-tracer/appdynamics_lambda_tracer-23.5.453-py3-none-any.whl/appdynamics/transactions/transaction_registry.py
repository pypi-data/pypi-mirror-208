import logging

from appdynamics.config.agent_config_response import AgentConfigResponse
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, OVERFLOW_TRANSACTION_NAME


class TransactionRegistry:
    """The TransactionRegistry class contains a registry of registered BTs.

    This class stores a registry(dict) of the registered BTs.
    It also provides a utility method to get the bt_id for a given entry_point_name and entry_point_type.

    Attributes:
        bt_registry: dictionary containing the registered BTs. The key being tuple of entry point name & type (<entry_point_name>, <entry_point_type>) and value being bt_id.
        logger: Reference to the python in-built logger.
    """

    def __init__(self):
        self.bt_registry = {}
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

    def update_bt_registry(self, agent_config_response: AgentConfigResponse) -> None:
        """Updates the bt_registry attribute with the registered BTs.
        The key is a tuple of entry point name & type (<entry_point_name>, <entry_point_type>) and value is bt_id.
        Args:
            agent_config_response: an instance of the class AgentConfigResponse which contains information about the controller and the registered tier.
        """
        if agent_config_response and agent_config_response.registered_bts:
            registered_bts = agent_config_response.registered_bts
            if isinstance(registered_bts, list):
                self.bt_registry = dict(((bt['entry_point_name'], bt['entry_point_type']), bt['bt_id']) for bt in registered_bts
                                        if (bt.get('entry_point_name') and bt.get('entry_point_type') and bt.get('bt_id')))
        return

    def get_bt_id(self, entry_point_name: str, entry_point_type: str) -> int:
        """Function to get a bt_id for a given entry point name and type
        Args:
            entry_point_name: Entry point name of the business transaction
            entry_point_type: Entry point type of the business transaction

        Returns:
            int: bt_id, if the entry_point_name and entry_point_type are found in the bt_registry
            0: if the entry_point_name and entry_point_type are not found in the bt_registry
        """
        if entry_point_name and entry_point_type:
            key = (entry_point_name, entry_point_type)
            if key in self.bt_registry:
                return self.bt_registry[key]
            self.logger.debug(
                f"BT with entry point name = {entry_point_name} and entry point type = {entry_point_type} not found in the BT registry")

        return 0

    def get_overflow_bt(self):
        overflow_bt_id = 0
        for key in self.bt_registry:
            entry_point_name = key[0]
            if entry_point_name.startswith(OVERFLOW_TRANSACTION_NAME):
                overflow_bt_id = self.bt_registry[key]
        return overflow_bt_id
