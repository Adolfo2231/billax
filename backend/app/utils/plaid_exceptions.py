class PlaidException(Exception):
    """Base exception for Plaid-related errors."""
    def __init__(self, message: str = "Plaid Error"):
        self.message = message

class PlaidTokenError(PlaidException):
    """Exception raised when Plaid token creation fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PlaidDataSyncError(PlaidException):
    """Exception raised when Plaid data sync fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PlaidUserNotLinkedError(PlaidException):
    """Exception raised when Plaid user is not linked."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PlaidUserAlreadyLinkedError(PlaidException):
    """Exception raised when Plaid user is already linked."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PlaidUserNotFoundError(PlaidException):
    """Exception raised when Plaid user is not found."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
