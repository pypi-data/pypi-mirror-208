import json
from datetime import datetime


class AgentConfigResponse:
    """
    TransactionContext will take in data from the agent config response and keep data from controller about current
    transaction.
    Attributes:
        transaction_registry: Reference to TransactionRegistry class where registered transaction details are kept.
        backend_registry: Reference to BackendRegistry class where registered backends' details are kept.
    """

    def __init__(self, transaction_registry, backend_registry):
        self._registered_bts = ""
        self._registered_backends = ""
        self._application_id = ""
        self._account_guid = ""
        self._tier_id = ""
        self._controller_guid = ""
        self._global_account_name = ""
        self._time_skew = 0
        self._is_lagging = None
        self.transaction_registry = transaction_registry
        self.backend_registry = backend_registry
        self._last_update_time_stamp = None
        self.utcnow = datetime.utcnow

    def update(self, agent_config_response):
        self.registered_bts = agent_config_response.get(
            'bts', self.registered_bts)
        self.registered_backends = agent_config_response.get(
            'backends', self.registered_backends)
        self.application_id = agent_config_response.get(
            'application_id', self.application_id)
        self.account_guid = agent_config_response.get(
            'account_guid', self.account_guid)
        self.tier_id = agent_config_response.get('tier_id', self.tier_id)
        self.controller_guid = agent_config_response.get(
            'controller_guid', self.controller_guid)
        self.global_account_name = agent_config_response.get(
            'global_account_name', self.global_account_name)
        self.time_skew = agent_config_response.get('time_skew', self.time_skew)
        self.is_lagging = agent_config_response.get('lagging', self.is_lagging)
        self.transaction_registry.update_bt_registry(self)
        self.backend_registry.update_registry(self.registered_backends)
        self.last_update_time_stamp = self.utcnow()

    @property
    def registered_bts(self):
        return self._registered_bts

    @registered_bts.setter
    def registered_bts(self, registered_bts):
        self._registered_bts = registered_bts

    @property
    def registered_backends(self):
        return self._registered_backends

    @registered_backends.setter
    def registered_backends(self, registered_backends):
        self._registered_backends = registered_backends

    @property
    def application_id(self):
        return self._application_id

    @application_id.setter
    def application_id(self, application_id):
        self._application_id = application_id

    @property
    def account_guid(self):
        return self._account_guid

    @account_guid.setter
    def account_guid(self, account_guid):
        self._account_guid = account_guid

    @property
    def tier_id(self):
        return self._tier_id

    @tier_id.setter
    def tier_id(self, tier_id):
        self._tier_id = tier_id

    @property
    def controller_guid(self):
        return self._controller_guid

    @controller_guid.setter
    def controller_guid(self, controller_guid):
        self._controller_guid = controller_guid

    @property
    def global_account_name(self):
        return self._global_account_name

    @global_account_name.setter
    def global_account_name(self, global_account_name):
        self._global_account_name = global_account_name

    @property
    def time_skew(self):
        return self._time_skew

    @time_skew.setter
    def time_skew(self, time_skew):
        self._time_skew = time_skew

    @property
    def is_lagging(self):
        return self._is_lagging

    @is_lagging.setter
    def is_lagging(self, is_lagging):
        self._is_lagging = is_lagging

    @property
    def last_update_time_stamp(self):
        return self._last_update_time_stamp

    @last_update_time_stamp.setter
    def last_update_time_stamp(self, last_update_time_stamp):
        self._last_update_time_stamp = last_update_time_stamp

    def get_skew_adjusted_start_wall_time(self):
        if self.is_lagging:
            return round(self.utcnow().timestamp() * 1000) + self.time_skew
        else:
            return round(self.utcnow().timestamp() * 1000) - self.time_skew

    def __str__(self):
        json_map = {
            "registered_bts": self.registered_bts,
            "registered_backends": self.registered_backends,
            "application_id": self.application_id,
            "account_guid": self.account_guid,
            "global_account_name": self.global_account_name,
            "tier_id": self.tier_id,
            "controller_guid": self.controller_guid,
            "time_skew": self.time_skew,
            "is_lagging": self.is_lagging
        }
        return json.dumps(json_map)
