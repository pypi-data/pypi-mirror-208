class TracerConfigurationError(Exception):
    def __init__(self, msg):
        self.msg = msg


class HttpServiceError(Exception):
    def __init__(self, msg):
        self.msg = msg


class TransactionValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg


class TracerEventError(Exception):
    def __init__(self, msg):
        self.msg = msg


class CorrelationHeaderError(Exception):
    def __init__(self, msg):
        self.msg = msg
