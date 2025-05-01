"""
Bank account repository for managing bank account data operations.

This module provides a repository class for managing bank account-related database operations.
It extends the BaseRepository class to provide bank account-specific functionality while
inheriting common CRUD operations.

The repository supports:
- Bank account creation and management
- User-specific account lookup
- Plaid account ID-based lookup
- Integration with BankAccount model
- Type-safe operations

Example:
    >>> bank_repo = BankAccountRepository()
    >>> accounts = bank_repo.get_by_user_id("user-123")
    >>> for account in accounts:
    ...     print(f"Account: {account.name} - Balance: ${account.current_balance}")
"""

from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.models.bank_account import BankAccount


class BankAccountRepository(BaseRepository[BankAccount]):
    """
    Repository class for managing bank account data operations.

    This class extends BaseRepository to provide bank account-specific database operations.
    It implements additional methods for bank account management while inheriting common
    CRUD operations from the base class.

    Attributes:
        model (Type[BankAccount]): The BankAccount model class that this repository operates on.

    Example:
        >>> bank_repo = BankAccountRepository()
        >>> accounts = bank_repo.get_by_user_id("user-123")
        >>> for account in accounts:
        ...     print(f"Account: {account.name} - Balance: ${account.current_balance}")
        Account: Checking - Balance: $1000.00
        Account: Savings - Balance: $5000.00
    """

    @property
    def model(self) -> type[BankAccount]:
        """
        Get the BankAccount model class.

        Returns:
            type[BankAccount]: The BankAccount model class.

        Example:
            >>> bank_repo = BankAccountRepository()
            >>> model = bank_repo.model
            >>> model.__name__
            'BankAccount'
        """
        return BankAccount

    def get_by_user_id(self, user_id: str) -> List[BankAccount]:
        """
        Get all bank accounts associated with a specific user.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            List[BankAccount]: A list of bank accounts belonging to the user.

        Example:
            >>> bank_repo = BankAccountRepository()
            >>> accounts = bank_repo.get_by_user_id("user-123")
            >>> for account in accounts:
            ...     print(f"Account: {account.name} - Balance: ${account.current_balance}")
            Account: Checking - Balance: $1000.00
            Account: Savings - Balance: $5000.00
        """
        return self.model.query.filter_by(user_id=user_id).all()

    def get_by_account_id(self, account_id: str) -> Optional[BankAccount]:
        """
        Get a bank account by its Plaid account ID.

        Args:
            account_id (str): The Plaid account identifier.

        Returns:
            Optional[BankAccount]: The bank account if found, None otherwise.

        Example:
            >>> bank_repo = BankAccountRepository()
            >>> account = bank_repo.get_by_account_id("acc_123")
            >>> if account:
            ...     print(f"Found account: {account.name}")
            ... else:
            ...     print("Account not found")
            Found account: Checking
        """
        return self.model.query.filter_by(account_id=account_id).first()
