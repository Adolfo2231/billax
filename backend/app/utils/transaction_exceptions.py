class TransactionNotFoundError(Exception):
    """Exception raised when a transaction is not found."""
    def __init__(self, message: str = "Transaction not found"):
        self.message = message
        super().__init__(self.message)

class TransactionTypeNotFoundError(Exception):
    """Exception raised when a transaction type is not found."""
    def __init__(self, message: str = "Transaction type not found"):
        self.message = message
        super().__init__(self.message)