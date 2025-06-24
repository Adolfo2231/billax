class TransactionNotFoundError(Exception):
    """Exception raised when a transaction is not found."""
    def __init__(self, message: str = "Transaction not found"):
        self.message = message
        super().__init__(self.message)