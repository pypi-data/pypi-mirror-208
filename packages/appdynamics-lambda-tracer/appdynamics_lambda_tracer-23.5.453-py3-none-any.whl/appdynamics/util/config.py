"""Config class holds all the required tracer configuration details.

Typical usage example:

    try:
        config = Config()
    except TracerConfigurationError as e:
        # Handle the exception
    except Exception as e:
        # Handle the exception
"""

import logging
import os
from hashlib import sha1, sha256

from appdynamics.util.constants import DEFAULT_AGENT_VERSION, DEFAULT_CONFIG_URL_PATH, DEFAULT_EVENT_URL_PATH, \
    DEFAULT_SERVERLESS_API_ENDPOINT_VERSION, ENV_APPDYNAMICS_ACCOUNT_NAME, ENV_APPDYNAMICS_AGENT_ACCOUNT_ACCESS_KEY, \
    ENV_APPDYNAMICS_APPLICATION_NAME, ENV_APPDYNAMICS_CONTROLLER_HOST, ENV_APPDYNAMICS_CONTROLLER_PORT, \
    ENV_APPDYNAMICS_TIER_NAME, ENV_LOG_LEVEL, ENV_SERVERLESS_API_ENDPOINT, HTTP_PROXY_HOST, HTTP_PROXY_PORT, \
    HTTP_PROXY_SERVER_CERTIFICATE_PATH, HTTP_PROXY_USER, HTTP_PROXY_PASSWORD, HTTP_PROXY_PASSWORD_FILE, \
    ENV_APPDYNAMICS_DISABLE_AGENT, ENV_APPDYNAMICS_HTTP_TIMEOUT_MS, HTTP_DEFAULT_TIMEOUT_MS, \
    APPDYNAMICS_LOGGER_NAME
from appdynamics.util.tracer_errors import TracerConfigurationError

REQUIRED_ENV_APPDYNAMICS_VARS = (ENV_APPDYNAMICS_CONTROLLER_HOST, ENV_APPDYNAMICS_AGENT_ACCOUNT_ACCESS_KEY,
                                 ENV_APPDYNAMICS_ACCOUNT_NAME, ENV_APPDYNAMICS_APPLICATION_NAME,
                                 ENV_SERVERLESS_API_ENDPOINT)

logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

class Config:
    def __init__(self):
        self._controller_host = ''
        self._controller_port = 443
        self._controller_access_key = ''
        self._account_name = ''
        self._application_name = ''
        self._tier_name = ''
        self._serverless_api_endpoint = ''
        self._tracer_version = ''
        self._log_level = logging.NOTSET
        self._routing_key = ''
        self._api_key = ''
        self._agent_config_url = ''
        self._events_url = ''
        self._http_timeout_secs = HTTP_DEFAULT_TIMEOUT_MS / 1000
        self.update_config()

    def update_config(self):
        validate_required_env_vars()
        self.controller_host = fetch_controller_host()
        self.controller_port = fetch_controller_port()
        self.controller_access_key = fetch_controller_access_key()
        self.account_name = fetch_account_name()
        self.application_name = fetch_application_name()
        self.tier_name = fetch_tier_name()
        self.serverless_api_endpoint = fetch_serverless_api_endpoint()
        self.tracer_version = fetch_tracer_version()
        self.log_level = fetch_log_level()
        self.routing_key = calculate_routing_key(self.controller_host, self.controller_port,
                                                 self.account_name, self.application_name, self.tier_name,
                                                 self.tracer_version)
        self.api_key = calculate_api_key(
            self.controller_access_key, self.account_name)
        self.agent_config_url = calculate_agent_config_url(
            self.serverless_api_endpoint)
        self.events_url = calculate_events_url(self.serverless_api_endpoint)
        self.http_timeout_secs = fetch_http_timeout_secs()

    @property
    def controller_host(self):
        return self._controller_host

    @controller_host.setter
    def controller_host(self, controller_host):
        self._controller_host = controller_host

    @property
    def controller_port(self):
        return self._controller_port

    @controller_port.setter
    def controller_port(self, controller_port):
        self._controller_port = controller_port

    @property
    def controller_access_key(self):
        return self._controller_access_key

    @controller_access_key.setter
    def controller_access_key(self, controller_access_key):
        self._controller_access_key = controller_access_key

    @property
    def account_name(self):
        return self._account_name

    @account_name.setter
    def account_name(self, account_name):
        self._account_name = account_name

    @property
    def application_name(self):
        return self._application_name

    @application_name.setter
    def application_name(self, application_name):
        self._application_name = application_name

    @property
    def tier_name(self):
        return self._tier_name

    @tier_name.setter
    def tier_name(self, tier_name):
        self._tier_name = tier_name

    @property
    def serverless_api_endpoint(self):
        return self._serverless_api_endpoint

    @serverless_api_endpoint.setter
    def serverless_api_endpoint(self, serverless_api_endpoint):
        self._serverless_api_endpoint = serverless_api_endpoint

    @property
    def tracer_version(self):
        return self._tracer_version

    @tracer_version.setter
    def tracer_version(self, tracer_version):
        self._tracer_version = tracer_version

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, log_level):
        self._log_level = log_level

    @property
    def routing_key(self):
        return self._routing_key

    @routing_key.setter
    def routing_key(self, routing_key):
        self._routing_key = routing_key

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        self._api_key = api_key

    @property
    def agent_config_url(self):
        return self._agent_config_url

    @agent_config_url.setter
    def agent_config_url(self, agent_config_url):
        self._agent_config_url = agent_config_url

    @property
    def events_url(self):
        return self._events_url

    @events_url.setter
    def events_url(self, events_url):
        self._events_url = events_url

    @property
    def http_timeout_secs(self):
        return self._http_timeout_secs

    @http_timeout_secs.setter
    def http_timeout_secs(self, http_timeout_secs):
        self._http_timeout_secs = http_timeout_secs


def validate_required_env_vars() -> None:
    missed_env_vars = [env_var for env_var in REQUIRED_ENV_APPDYNAMICS_VARS if env_var not in os.environ]
    if len(missed_env_vars) > 0:
        raise TracerConfigurationError('Missing required environment variables {}'.format(missed_env_vars))

    empty_env_vars = [env_var for env_var in REQUIRED_ENV_APPDYNAMICS_VARS if not os.environ[env_var]]
    if len(empty_env_vars) > 0:
        raise TracerConfigurationError('Required environment variables with empty string {}'.format(empty_env_vars))


def strip_whitespace_slash(data: str) -> str:
    return data.strip(" /\\")


def fetch_controller_host() -> str:
    return strip_whitespace_slash(os.environ[ENV_APPDYNAMICS_CONTROLLER_HOST])


def fetch_controller_port() -> int:
    port = 443
    if ENV_APPDYNAMICS_CONTROLLER_PORT in os.environ:
        try:
            port = int(os.environ[ENV_APPDYNAMICS_CONTROLLER_PORT])
        except ValueError:
            raise TracerConfigurationError('APPDYNAMICS_CONTROLLER_PORT={} is not a parsable integer.'
                                           .format(os.environ[ENV_APPDYNAMICS_CONTROLLER_PORT]))
        if port < 1 or port > 65535:
            raise TracerConfigurationError('APPDYNAMICS_CONTROLLER_PORT={} is not in valid port range.'
                                           .format(os.environ[ENV_APPDYNAMICS_CONTROLLER_PORT]))
    return port


def fetch_controller_access_key() -> str:
    return os.environ[ENV_APPDYNAMICS_AGENT_ACCOUNT_ACCESS_KEY].strip()


def fetch_account_name() -> str:
    return os.environ[ENV_APPDYNAMICS_ACCOUNT_NAME].strip()


def fetch_application_name() -> str:
    return os.environ[ENV_APPDYNAMICS_APPLICATION_NAME].strip()


def fetch_tier_name() -> str:
    if ENV_APPDYNAMICS_TIER_NAME in os.environ:
        return os.environ[ENV_APPDYNAMICS_TIER_NAME].strip()
    else:
        return os.environ['AWS_LAMBDA_FUNCTION_NAME'] + '-' + os.environ['AWS_LAMBDA_FUNCTION_VERSION']


def fetch_serverless_api_endpoint() -> str:
    return strip_whitespace_slash(os.environ[ENV_SERVERLESS_API_ENDPOINT])


def fetch_log_level() -> int:
    # default log level is 'info'
    desired_log_level_str = 'info'
    if ENV_LOG_LEVEL in os.environ:
        desired_log_level_str = os.environ[ENV_LOG_LEVEL].strip().lower()
    
    log_level_map = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    return log_level_map.get(desired_log_level_str, logging.INFO)


def fetch_tracer_version() -> str:
    try:
        tracer_version = DEFAULT_AGENT_VERSION
        return tracer_version
    except AttributeError:
        raise TracerConfigurationError(
            'Missing required constant DEFAULT_AGENT_VERSION')


def fetch_proxy_host() -> str:
    host = os.environ.get(HTTP_PROXY_HOST)
    if host:
        return strip_whitespace_slash(host)


def fetch_proxy_port() -> str:
    port = os.environ.get(HTTP_PROXY_PORT)
    if port:
        return port.strip()


def fetch_proxy_user() -> str:
    user = os.environ.get(HTTP_PROXY_USER)
    if user:
        return user.strip()


def fetch_proxy_cert_path() -> str:
    path = os.environ.get(HTTP_PROXY_SERVER_CERTIFICATE_PATH)
    if path:
        return path.strip()


def fetch_proxy_password() -> str:
    password = os.environ.get(HTTP_PROXY_PASSWORD)
    if password:
        return password.strip()


def fetch_proxy_password_file() -> str:
    password_file = os.environ.get(HTTP_PROXY_PASSWORD_FILE)
    if password_file:
        return password_file.strip()


def fetch_http_timeout_secs() -> float:
    timeout = HTTP_DEFAULT_TIMEOUT_MS
    if ENV_APPDYNAMICS_HTTP_TIMEOUT_MS in os.environ:
        try:
            timeout = int(os.environ[ENV_APPDYNAMICS_HTTP_TIMEOUT_MS])
        except ValueError:
            logger.warning(f"{ENV_APPDYNAMICS_HTTP_TIMEOUT_MS}={os.environ[ENV_APPDYNAMICS_HTTP_TIMEOUT_MS]} supplied is not a valid int, "
                           f"defaulting to {HTTP_DEFAULT_TIMEOUT_MS} ms")
            timeout = HTTP_DEFAULT_TIMEOUT_MS
    return timeout / 1000
        

def is_tracer_disabled():
    return os.environ.get(ENV_APPDYNAMICS_DISABLE_AGENT, "").strip().lower() == 'true'


def calculate_routing_key(controller_host: str, controller_port: int, account_name: str, application_name: str,
                          tier_name: str, tracer_version: str) -> str:
    separator = '|'
    routing_key_components = [
        controller_host,
        str(controller_port),
        account_name,
        application_name,
        tier_name,
        tracer_version
    ]
    routing_key_string = separator.join(routing_key_components)
    routing_key_hash = sha1(routing_key_string.encode())
    routing_key = routing_key_hash.hexdigest()
    return routing_key


def calculate_api_key(controller_access_key: str, account_name: str) -> str:
    api_key_string = controller_access_key + '-' + account_name
    api_key_hash = sha256(api_key_string.encode())
    api_key = api_key_hash.hexdigest()
    return api_key


def calculate_agent_config_url(serverless_api_endpoint: str) -> str:
    return serverless_api_endpoint + '/' + DEFAULT_SERVERLESS_API_ENDPOINT_VERSION + '/' + DEFAULT_CONFIG_URL_PATH


def calculate_events_url(serverless_api_endpoint: str) -> str:
    return serverless_api_endpoint + '/' + DEFAULT_SERVERLESS_API_ENDPOINT_VERSION + '/' + DEFAULT_EVENT_URL_PATH
