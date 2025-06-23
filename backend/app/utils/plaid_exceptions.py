class PlaidException(Exception):
    """Base exception for Plaid-related errors."""
    def __init__(self, message: str = "Plaid Error"):
        self.message = message
        super().__init__(self.message)

class PlaidTokenError(PlaidException):
    """Exception raised when Plaid token creation fails."""
    def __init__(self, message: str = "Plaid token error"):
        super().__init__(message)

class PlaidDataSyncError(PlaidException):
    """Exception raised when Plaid data sync fails."""
    def __init__(self, message: str = "Plaid data sync error"):
        super().__init__(message)

class PlaidUserNotLinkedError(PlaidException):
    """Exception raised when Plaid user is not linked."""
    def __init__(self, message: str = "User is not linked to Plaid"):
        super().__init__(message)

class PlaidUserAlreadyLinkedError(PlaidException):
    """Exception raised when Plaid user is already linked."""
    def __init__(self, message: str = "User is already linked to Plaid"):
        super().__init__(message)

class PlaidUserNotFoundError(PlaidException):
    """Exception raised when Plaid user is not found."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message)
