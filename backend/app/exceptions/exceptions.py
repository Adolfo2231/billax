"""
Custom Exceptions for Financial Application Error Handling.

This module defines custom exceptions for handling various error scenarios
in the financial application. Each exception class includes automatic
error logging and provides clear, descriptive error messages.

Key Features:
- Automatic error logging
- Descriptive error messages
- Type-safe exception handling
- Business logic validation
- API integration error handling

Example:
    >>> try:
    ...     if balance < amount:
    ...         raise InsufficientBalanceError()
    ... except InsufficientBalanceError as e:
    ...     print(f"Error: {e}")
    ...     # Error will be automatically logged
    Error: Insufficient balance to complete this transaction.
"""

import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class InsufficientBalanceError(Exception):
    """
    Exception raised when a transaction cannot be completed due to
    insufficient funds in the account.

    This exception is raised when attempting to perform a transaction
    that would result in a negative balance or exceed available funds.

    Attributes:
        message (str): A descriptive error message explaining the
            insufficient balance condition.

    Example:
        >>> try:
        ...     if account.balance < transaction.amount:
        ...         raise InsufficientBalanceError()
        ... except InsufficientBalanceError as e:
        ...     print(f"Transaction failed: {e}")
        Transaction failed: Insufficient balance to complete this transaction.
    """

    def __init__(self, message: str = "Insufficient balance to complete this transaction."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidEmailError(Exception):
    """
    Exception raised when an invalid email address is provided.

    This exception is raised during user registration or email updates
    when the provided email address does not meet validation criteria.

    Attributes:
        message (str): A descriptive error message explaining the
            email validation failure.

    Example:
        >>> try:
        ...     if not is_valid_email(email):
        ...         raise InvalidEmailError()
        ... except InvalidEmailError as e:
        ...     print(f"Invalid email: {e}")
        Invalid email: The email address provided is invalid.
    """

    def __init__(self, message: str = "The email address provided is invalid."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class DuplicateEmailError(Exception):
    """
    Exception raised when attempting to register an email that is
    already in use.

    This exception is raised during user registration when the provided
    email address is already associated with an existing account.

    Attributes:
        message (str): A descriptive error message indicating the
            email duplication.

    Example:
        >>> try:
        ...     if email_exists(email):
        ...         raise DuplicateEmailError()
        ... except DuplicateEmailError as e:
        ...     print(f"Registration failed: {e}")
        Registration failed: This email is already registered.
    """

    def __init__(self, message: str = "This email is already registered."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidNameError(Exception):
    """
    Exception raised when an invalid name is provided.

    This exception is raised during user registration or profile updates
    when the provided name does not meet validation criteria.

    Attributes:
        message (str): A descriptive error message explaining the
            name validation failure.

    Example:
        >>> try:
        ...     if not is_valid_name(name):
        ...         raise InvalidNameError()
        ... except InvalidNameError as e:
        ...     print(f"Invalid name: {e}")
        Invalid name: The name must be at least 2 characters and only contain letters and spaces.
    """

    def __init__(self, message: str = "The name must be at least 2 characters and only contain letters and spaces."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidPasswordError(Exception):
    """
    Exception raised when an invalid password is provided.

    This exception is raised during user registration or password updates
    when the provided password does not meet security requirements.

    Attributes:
        message (str): A descriptive error message explaining the
            password validation failure.

    Example:
        >>> try:
        ...     if not is_valid_password(password):
        ...         raise InvalidPasswordError()
        ... except InvalidPasswordError as e:
        ...     print(f"Invalid password: {e}")
        Invalid password: Password must be at least 6 characters long.
    """

    def __init__(self, message: str = "Password must be at least 6 characters long."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class BankAccountNotFoundError(Exception):
    """
    Exception raised when a requested bank account cannot be found.

    This exception is raised when attempting to access a bank account
    that does not exist or is not associated with the current user.

    Attributes:
        message (str): A descriptive error message indicating the
            account was not found.

    Example:
        >>> try:
        ...     account = get_account(account_id)
        ...     if not account:
        ...         raise BankAccountNotFoundError()
        ... except BankAccountNotFoundError as e:
        ...     print(f"Account error: {e}")
        Account error: Bank account not found.
    """

    def __init__(self, message: str = "Bank account not found."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidAmountError(Exception):
    """
    Exception raised when an invalid amount is provided for a transaction.

    This exception is raised when attempting to create a transaction
    with an invalid or negative amount.

    Attributes:
        message (str): A descriptive error message explaining the
            amount validation failure.

    Example:
        >>> try:
        ...     if amount <= 0:
        ...         raise InvalidAmountError()
        ... except InvalidAmountError as e:
        ...     print(f"Invalid amount: {e}")
        Invalid amount: Amount must be a number greater than 0.
    """

    def __init__(self, message: str = "Amount must be a number greater than 0."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidTransactionTypeError(Exception):
    """
    Exception raised when an invalid transaction type is provided.

    This exception is raised when attempting to create a transaction
    with an invalid type that is not 'Income' or 'Expense'.

    Attributes:
        message (str): A descriptive error message explaining the
            transaction type validation failure.

    Example:
        >>> try:
        ...     if transaction_type not in ['Income', 'Expense']:
        ...         raise InvalidTransactionTypeError()
        ... except InvalidTransactionTypeError as e:
        ...     print(f"Invalid type: {e}")
        Invalid type: Transaction type must be either 'Income' or 'Expense'.
    """

    def __init__(self, message: str = "Transaction type must be either 'Income' or 'Expense'."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class UnauthorizedAccessError(Exception):
    """
    Exception raised when a user attempts to access resources they
    are not authorized to access.

    This exception is raised when a user tries to access accounts,
    transactions, or other resources that belong to another user.

    Attributes:
        message (str): A descriptive error message indicating the
            unauthorized access attempt.

    Example:
        >>> try:
        ...     if not has_access(user_id, resource_id):
        ...         raise UnauthorizedAccessError()
        ... except UnauthorizedAccessError as e:
        ...     print(f"Access denied: {e}")
        Access denied: You are not authorized to access this account or transaction.
    """

    def __init__(self, message: str = "You are not authorized to access this account or transaction."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class InvalidDateFormatError(Exception):
    """
    Exception raised when an invalid date format is provided.

    This exception is raised when attempting to process dates that
    are not in the required YYYY-MM-DD format.

    Attributes:
        message (str): A descriptive error message explaining the
            date format validation failure.

    Example:
        >>> try:
        ...     if not is_valid_date_format(date_str):
        ...         raise InvalidDateFormatError()
        ... except InvalidDateFormatError as e:
        ...     print(f"Invalid date: {e}")
        Invalid date: Date format must be YYYY-MM-DD.
    """

    def __init__(self, message: str = "Date format must be YYYY-MM-DD."):
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class APIConnectionError(Exception):
    """
    Exception raised when there is an error connecting to an external API.

    This exception is raised when there are issues connecting to or
    communicating with external APIs, such as Plaid or other financial
    service providers.

    Attributes:
        api_name (str): The name of the API that failed to connect
        message (str): A descriptive error message explaining the
            connection failure

    Example:
        >>> try:
        ...     response = plaid_client.get_transactions()
        ... except Exception as e:
        ...     raise APIConnectionError('Plaid', str(e))
        ... except APIConnectionError as e:
        ...     print(f"API error: {e}")
        API error: Error connecting to Plaid API: Connection timeout
    """

    def __init__(self, api_name: str, message: str):
        self.api_name = api_name
        self.message = message
        super().__init__(f"Error connecting to {api_name} API: {message}")
        logging.error(f"API Connection Error - {api_name}: {message}")

    def __str__(self) -> str:
        return f"Error connecting to {self.api_name} API: {self.message}"
