"""
Transaction repository for managing transaction data operations.

This module provides a repository class for managing transaction-related database operations.
It extends the BaseRepository class to provide transaction-specific functionality while
inheriting common CRUD operations.

The repository supports:
- Transaction creation and management
- Plaid transaction ID-based lookup
- Account-specific transaction lookup
- Date range-based transaction filtering
- Pending transaction management
- Integration with Transaction model
- Type-safe operations

Example:
    >>> trans_repo = TransactionRepository()
    >>> transactions = trans_repo.get_by_date_range("2024-03-01", "2024-03-31")
    >>> for transaction in transactions:
    ...     print(f"Transaction: {transaction.name} - Amount: ${transaction.amount}")
    Transaction: Grocery Store - Amount: $50.00
    Transaction: Restaurant - Amount: $30.00
"""

from typing import List, Optional
from datetime import date
from app.repositories.base_repository import BaseRepository
from app.models.transaction import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository class for managing transaction data operations.

    This class extends BaseRepository to provide transaction-specific database operations.
    It implements additional methods for transaction management while inheriting common
    CRUD operations from the base class.

    Attributes:
        model (Type[Transaction]): The Transaction model class that this repository operates on.

    Example:
        >>> trans_repo = TransactionRepository()
        >>> transactions = trans_repo.get_by_date_range("2024-03-01", "2024-03-31")
        >>> for transaction in transactions:
        ...     print(f"Transaction: {transaction.name} - Amount: ${transaction.amount}")
        Transaction: Grocery Store - Amount: $50.00
        Transaction: Restaurant - Amount: $30.00
    """

    @property
    def model(self) -> type[Transaction]:
        """
        Get the Transaction model class.

        Returns:
            type[Transaction]: The Transaction model class.

        Example:
            >>> trans_repo = TransactionRepository()
            >>> model = trans_repo.model
            >>> model.__name__
            'Transaction'
        """
        return Transaction

    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction by its Plaid transaction ID.

        Args:
            transaction_id (str): The unique Plaid transaction identifier.

        Returns:
            Optional[Transaction]: The transaction if found, None otherwise.

        Example:
            >>> trans_repo = TransactionRepository()
            >>> transaction = trans_repo.get_by_transaction_id("txn_123")
            >>> if transaction:
            ...     print(f"Found transaction: {transaction.name}")
            ... else:
            ...     print("Transaction not found")
            Found transaction: Grocery Store
        """
        return self.model.query.filter_by(transaction_id=transaction_id).first()

    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        """
        Get all transactions associated with a specific bank account.

        Args:
            account_id (str): The Plaid account identifier.

        Returns:
            List[Transaction]: A list of transactions for the specified account.

        Example:
            >>> trans_repo = TransactionRepository()
            >>> transactions = trans_repo.get_by_account_id("acc_123")
            >>> for transaction in transactions:
            ...     print(f"Transaction: {transaction.name} - Amount: ${transaction.amount}")
            Transaction: Grocery Store - Amount: $50.00
            Transaction: Restaurant - Amount: $30.00
        """
        return self.model.query.filter_by(account_id=account_id).all()

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """
        Get all transactions within a specific date range.

        Args:
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            List[Transaction]: A list of transactions within the specified date range.

        Example:
            >>> trans_repo = TransactionRepository()
            >>> transactions = trans_repo.get_by_date_range("2024-03-01", "2024-03-31")
            >>> for transaction in transactions:
            ...     print(f"Transaction: {transaction.name} - Date: {transaction.date}")
            Transaction: Grocery Store - Date: 2024-03-15
            Transaction: Restaurant - Date: 2024-03-20
        """
        return self.model.query.filter(
            self.model.date >= start_date,
            self.model.date <= end_date
        ).all()

    def get_pending(self) -> List[Transaction]:
        """
        Get all pending transactions.

        Returns:
            List[Transaction]: A list of pending transactions.

        Example:
            >>> trans_repo = TransactionRepository()
            >>> pending = trans_repo.get_pending()
            >>> for transaction in pending:
            ...     print(f"Pending: {transaction.name} - Amount: ${transaction.amount}")
            Pending: Restaurant - Amount: $30.00
        """
        return self.model.query.filter_by(pending=True).all()
