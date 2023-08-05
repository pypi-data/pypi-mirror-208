import os
import logging

from httpx import AsyncClient, HTTPError, TimeoutException

from appdynamics.util.config import fetch_proxy_host, fetch_proxy_port, fetch_proxy_user, \
    fetch_proxy_password, fetch_proxy_password_file, fetch_proxy_cert_path
from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME, HTTP_DEFAULT_TIMEOUT_MS
from appdynamics.util.tracer_errors import HttpServiceError
from appdynamics.util.file_tools import create_valid_lambda_path, read_lambda_file

class HttpService:
    """ Service Class to make asynchronous http requests.
    """

    def __init__(self):
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)
        self.proxy_url = None
        self.proxy_cert_path = True  # HTTPX default param for no proxy cert is True.
        self.setup_proxy()

    async def post(self, url, headers, payload, connection_timeout=HTTP_DEFAULT_TIMEOUT_MS / 1000):
        """ Function is used to make a asynchronous http post request.

        Args:
            url: HTTP Rest url
            headers: HTTP headers
            payload: JSON payload
        """
        try:
            async with AsyncClient(proxies=self.proxy_url, verify=self.proxy_cert_path) as client:
                response = await client.post(url, data=payload, headers=headers, timeout=connection_timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") is None:
                        self.logger.info(f"HTTP post request was successful for url {url}")
                        self.logger.debug(f"Successful response: {data}")
                        return data
                    else:
                        error_msg = data.get('error')
                        # We want to log all errors from router as info log level.
                        # For example: benign errors like reporter idle, inital ETIMEDOUT, ECONNREFUSED etc
                        # This is to avoid unnecessary confusion among customers.
                        self.logger.info(f"HTTP post request message: {error_msg}")
                        raise HttpServiceError(f"Error occurred in HTTPX post request: {error_msg}")
                else:
                    self.logger.error(f"Error occurred on HTTP post request. Status code: {response.status_code} "
                                      f"message: {response.reason_phrase}")
                    raise HttpServiceError('Error occurred: Non-200 response in HTTPX post request.')

        except TimeoutException as e:
            self.logger.error(f"HTTPX POST request timed out for url {url}, timeout was configured to be {connection_timeout} seconds: {e}")
            raise HttpServiceError(f"HTTPX post request failed. HTTPX TimeoutException occured.")

        except HTTPError as e:
            self.logger.error(f"HTTPX HTTPError: {e}")
            raise HttpServiceError('HTTPX post request failed. HTTPX HTTPError occurred.')

    def setup_proxy(self):
        proxy_host = fetch_proxy_host()
        proxy_port = fetch_proxy_port()
        http_proxy_server_certificate = fetch_proxy_cert_path()
        user = fetch_proxy_user()
        password = fetch_proxy_password()
        password_file = fetch_proxy_password_file()

        if proxy_host and proxy_port:
            if password_file:
                contents = read_lambda_file(password_file)
                if contents:
                    self.logger.debug(f"Setting password to contents of password file at {password_file}.")
                    password = contents
                else:
                    self.logger.warning(f"Could not load password file at {password_file}. Will use existing password.")
            if user and password:
                proxy_url = {
                    "http": f"http://{user}:{password}@{proxy_host}:{proxy_port}",
                    "https": f"http://{user}:{password}@{proxy_host}:{proxy_port}"
                }
            else:
                proxy_url = {
                    "http": f"http://{proxy_host}:{proxy_port}",
                    "https": f"http://{proxy_host}:{proxy_port}"
                }

            cert_path = create_valid_lambda_path(http_proxy_server_certificate)
            if cert_path:
                self.logger.debug(f"Successfully loaded proxy certificate with path: {cert_path}.")
                self.proxy_cert_path = cert_path
            elif http_proxy_server_certificate:
                self.logger.error(f"Tracer could not find provided file path: {http_proxy_server_certificate}. "
                                  f"Will not use Python proxy.")
                return

            self.proxy_url = proxy_url
            self.logger.info("Setup Python Tracer proxy.")

        elif proxy_host or proxy_port:
            if proxy_host:
                self.logger.error("[HTTP Service]: Missing required configuration proxyPort. proxyPort can be set "
                                  "either through options or environment variable APPDYNAMICS_HTTP_PROXY_PORT")
            else:
                self.logger.error("[HTTP Service]: Missing required configuration proxyHost. proxyHost can be set "
                                  "either through options or environment variable APPDYNAMICS_HTTP_PROXY_HOST")

        else:
            self.logger.debug("Proxy host and port not found. Proxy will not be setup.")
