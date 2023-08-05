import datetime
import logging
import os
from urllib.parse import quote, urlparse

from appdynamics.util.constants import ADRUM_PREFIX, EUM_COOKIE_EXPIRATION_DURATION, CLIENT_REQUEST_GUID_KEY, \
    GLOBAL_ACCOUNT_NAME_KEY, BT_ID_KEY, BT_DURATION_KEY, ADRUM_MASTER_COOKIE_NAME, APPDYNAMICS_LOGGER_NAME, \
    ENV_APPDYNAMICS_EUM_AJAX
from appdynamics.transactions.transaction import Transaction

SHORT_KEY = "short"
LONG_KEY = "long"

# Safe characters for urllib.parse.quote()
SAFE_CHARS = "~()*!.\'"

class EUMCookie:

    # Note: eum is of type 'EUM' which is a forward reference:
    # (https://www.python.org/dev/peps/pep-0484/#forward-references)
    # This is because EUM can't be imported because of circular dependency (eum.py already imports eum_cookie.py)
    def __init__(self, eum: 'EUM', transaction: Transaction, req_headers: dict, lambda_response: dict):
        self.logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

        self.eum = eum
        self.transaction = transaction
        self.req_headers = req_headers
        self.lambda_response = lambda_response
        self.is_https = (req_headers is not None and 
                         "X-Forwarded-Proto" in req_headers and 
                         req_headers["X-Forwarded-Proto"] == "https")

        self.is_ajax: bool = None
        self.is_mobile: bool = None
        self.ajax_header_counter = 0

        self.cookie_value: str = None
        self.keyform = SHORT_KEY
        self.guid: str = None

    def set_ajax_call(self, value: bool) -> None:
        self.is_ajax = value
    
    def add_sub_cookie(self, name: str, value: str) -> None:
        self.logger.debug(f"add_sub_cookie -  Name: {name}, Value: {value}")

        if self.is_ajax:
            header_name = f"{ADRUM_PREFIX}{self.ajax_header_counter}"
            self.ajax_header_counter += 1
            if "headers" not in self.lambda_response:
                self.lambda_response["headers"] = {}
            # Note: The added safe chars ensures that quote() behaves identically to encodeURIComponent
            # see: https://stackoverflow.com/questions/946170/equivalent-javascript-functions-for-pythons-urllib-quote-and-urllib-unquote
            self.lambda_response["headers"][header_name] = f"{name}:{quote(value, safe=SAFE_CHARS)}"
        else:
            if self.cookie_value is None and self.req_headers is not None:
                referer = self.req_headers.get("referer") or self.req_headers.get("Referer")
                referer_length = len(referer) if referer is not None else 0
                self.cookie_value = f"R:{referer_length}"

            self.cookie_value += f"|{name}:{quote(value, safe=SAFE_CHARS)}"

    def set_cookie_header(self, name: str, value: str) -> None:
        pairs = [f"{name}={value}"]

        pairs.append("Path=/")

        timenow_utc = datetime.datetime.now(datetime.timezone.utc)
        expiration = timenow_utc + datetime.timedelta(milliseconds=EUM_COOKIE_EXPIRATION_DURATION)
        expiration_string = expiration.strftime("%a, %d %b %Y %H:%M:%S GMT")
        pairs.append(f"Expires={expiration_string}")

        if self.is_https:
            pairs.append("Secure")

        rum_cookie = "; ".join(pairs)
        cookies = rum_cookie

        self.logger.debug(f"set_cookie_header - Setting cookie: {rum_cookie}")

        if (self.lambda_response is not None and 
            "multiValueHeaders" in self.lambda_response and 
            "Set-Cookie" in self.lambda_response["multiValueHeaders"]):

            cookies = self.lambda_response["multiValueHeaders"]["Set-Cookie"].append(rum_cookie)
        elif (self.lambda_response is not None and
              "headers" in self.lambda_response and
              "Set-Cookie" in self.lambda_response["headers"]):
            
            cookies = [self.lambda_response["headers"]["Set-Cookie"], rum_cookie]
            del self.lambda_response["headers"]["Set-Cookie"]


        if isinstance(cookies, list):
            self.logger.debug("set_cookie_header - Setting multiple value headers")
            if "multiValueHeaders" not in self.lambda_response:
                self.lambda_response["multiValueHeaders"] = {}
            self.lambda_response["multiValueHeaders"]["Set-Cookie"] = cookies
        else:
            self.logger.debug("set_cookie_header = Setting single value header")
            if "headers" not in self.lambda_response:
                self.lambda_response["headers"] = {}
            self.lambda_response["headers"]["Set-Cookie"] = cookies

    def set_field_values(self) -> None:
        guid = self.eum.generate_guid()
        self.add_sub_cookie(CLIENT_REQUEST_GUID_KEY[self.keyform], guid)

        gan = self.eum.get_global_account_name()
        if gan:
            self.add_sub_cookie(GLOBAL_ACCOUNT_NAME_KEY[self.keyform], gan)

        #Note: The bt_id field must appear before the duration field. (From EumMetadataCollector.java in the Java lambda tracer)
        if self.transaction.bt_id:
            self.add_sub_cookie(BT_ID_KEY[self.keyform], str(self.transaction.bt_id))
        
        if self.transaction.start_time and self.transaction.end_time:
            duration = self.transaction.end_time - self.transaction.start_time
            self.add_sub_cookie(BT_DURATION_KEY[self.keyform], str(duration))

        # if is_ajax then headers already set
        if not self.is_ajax:
            self.set_cookie_header(ADRUM_MASTER_COOKIE_NAME, self.cookie_value)

    def build(self) -> None:
        adrum_header = self.req_headers.get("adrum") if self.req_headers else None

        if ENV_APPDYNAMICS_EUM_AJAX in os.environ:
            self.is_ajax = os.environ[ENV_APPDYNAMICS_EUM_AJAX].strip().lower() == "true"
            
        if self.is_ajax is None:
            self.is_ajax = adrum_header is not None and adrum_header.find("isAjax:true") != -1

            # If the referer header doesn't match the Host header then
            # classify it as AJAX request
            if self.req_headers and ("referer" in self.req_headers or "Referer" in self.req_headers):
                referer_url = self.req_headers.get("referer") or self.req_headers.get("Referer")
                #Note: urlparse returns a named tuple
                referer_host = urlparse(referer_url).hostname
                if referer_host != self.req_headers.get("Host"):
                    self.is_ajax = True
        
        adrum_header1 = self.req_headers.get("adrum_1") if self.req_headers else None
        self.is_mobile = adrum_header1 is not None and adrum_header1.find("isMobile:true") != -1

        if self.is_mobile:
            self.keyform = LONG_KEY
        self.set_field_values()