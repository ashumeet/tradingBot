class OrderValidationError(Exception):
    def __init__(self, message, details=None):
        self.code = "order_validation_error"
        self.message = message
        self.details = details
        super().__init__(message)

class AlpacaApiError(Exception):
    def __init__(self, message, details=None):
        self.code = "alpaca_api_error"
        self.message = message
        self.details = details
        super().__init__(message)

class InternalServerError(Exception):
    def __init__(self, message="Internal server error", details=None):
        self.code = "internal_server_error"
        self.message = message
        self.details = details
        super().__init__(message) 