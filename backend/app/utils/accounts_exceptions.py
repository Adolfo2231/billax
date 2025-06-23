class AccountNotFoundError(Exception):
    """Exception raised when an account is not found."""
    def __init__(self, message: str = "Account not found"):
        self.message = message
        super().__init__(self.message)