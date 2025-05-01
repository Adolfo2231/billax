"""
Transaction Facade for managing financial transactions.

This module provides a facade class that handles business logic related to financial transactions.
It acts as an intermediary between the API layer and the database, managing:
- Transaction creation and updates
- Transaction retrieval and filtering
- Transaction synchronization with Plaid
- Database transaction management

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facade.transaction_facade import TransactionFacade
    >>> # Get transactions for an account
    >>> transactions = TransactionFacade.get_transactions_by_account("acc-123")
    >>> print(f"Found {len(transactions)} transactions")
    Found 50 transactions
"""

from app.models.transaction import Transaction
from app import db
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

class TransactionFacade:
    """
    Business logic layer for handling financial transactions.

    This class provides a simplified interface for managing transactions in the system.
    It handles all database operations related to transactions, including creation,
    updates, retrieval, and synchronization with external services like Plaid.

    Example:
        >>> # Get transactions for a date range
        >>> start_date = "2024-03-01"
        >>> end_date = "2024-03-31"
        >>> transactions = TransactionFacade.get_transactions_by_date_range(
        ...     "acc-123",
        ...     start_date,
        ...     end_date
        ... )
        >>> print(f"Found {len(transactions)} transactions in March")
        Found 25 transactions in March
    """

    @staticmethod
    def get_all_transactions() -> List[Transaction]:
        """
        Get all transactions from the database.

        Returns:
            List[Transaction]: A list of all transactions in the system.

        Example:
            >>> transactions = TransactionFacade.get_all_transactions()
            >>> print(f"Total transactions: {len(transactions)}")
            Total transactions: 1000
        """
        return Transaction.query.all()

    @staticmethod
    def get_transaction_by_id(transaction_id: str) -> Optional[Transaction]:
        """
        Get a specific transaction by its ID.

        Args:
            transaction_id (str): The unique identifier of the transaction.

        Returns:
            Optional[Transaction]: The transaction if found, None otherwise.

        Example:
            >>> transaction = TransactionFacade.get_transaction_by_id("txn-123")
            >>> if transaction:
            ...     print(f"Found transaction: {transaction.name} - ${transaction.amount}")
            ... else:
            ...     print("Transaction not found")
            Found transaction: Grocery Store - $75.50
        """
        return Transaction.query.filter_by(transaction_id=transaction_id).first()

    @staticmethod
    def get_transactions_by_account(account_id: str) -> List[Transaction]:
        """
        Get all transactions for a specific account.

        Args:
            account_id (str): The ID of the account whose transactions to retrieve.

        Returns:
            List[Transaction]: A list of transactions for the account.

        Example:
            >>> transactions = TransactionFacade.get_transactions_by_account("acc-123")
            >>> print(f"Account has {len(transactions)} transactions")
            Account has 50 transactions
        """
        return Transaction.query.filter_by(account_id=account_id).all()

    @staticmethod
    def get_transactions_by_date_range(
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Transaction]:
        """
        Get transactions for a specific account within a date range.

        Args:
            account_id (str): The ID of the account.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            List[Transaction]: A list of transactions within the date range.

        Example:
            >>> transactions = TransactionFacade.get_transactions_by_date_range(
            ...     "acc-123",
            ...     "2024-03-01",
            ...     "2024-03-31"
            ... )
            >>> print(f"Found {len(transactions)} transactions in March")
            Found 25 transactions in March
        """
        return Transaction.query.filter(
            Transaction.account_id == account_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()

    @staticmethod
    def create_transaction(
        transaction_id: str,
        account_id: str,
        name: str,
        amount: float,
        date: str,
        category: Optional[List[str]] = None,
        pending: bool = False,
        merchant_name: Optional[str] = None,
        payment_channel: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Create a new transaction.

        Args:
            transaction_id (str): The unique identifier for the transaction.
            account_id (str): The ID of the account this transaction belongs to.
            name (str): The name/description of the transaction.
            amount (float): The amount of the transaction.
            date (str): The date of the transaction in YYYY-MM-DD format.
            category (Optional[List[str]]): List of categories for the transaction.
            pending (bool): Whether the transaction is pending.
            merchant_name (Optional[str]): The name of the merchant.
            payment_channel (Optional[str]): The payment channel used.
            location (Optional[Dict[str, Any]]): Location information for the transaction.

        Returns:
            Transaction: The newly created transaction.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> transaction = TransactionFacade.create_transaction(
            ...     transaction_id="txn-123",
            ...     account_id="acc-123",
            ...     name="Grocery Store",
            ...     amount=75.50,
            ...     date="2024-03-15",
            ...     category=["Food", "Groceries"],
            ...     merchant_name="Whole Foods",
            ...     payment_channel="in store",
            ...     location={"city": "San Francisco", "state": "CA"}
            ... )
            >>> print(f"Created transaction: {transaction.name} - ${transaction.amount}")
            Created transaction: Grocery Store - $75.50
        """
        try:
            transaction = Transaction(
                transaction_id=transaction_id,
                account_id=account_id,
                name=name,
                amount=amount,
                date=date,
                category=category,
                pending=pending,
                merchant_name=merchant_name,
                payment_channel=payment_channel,
                location=location
            )

            db.session.add(transaction)
            db.session.commit()
            return transaction
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_transaction(
        transaction_id: str,
        name: Optional[str] = None,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        category: Optional[List[str]] = None,
        pending: Optional[bool] = None,
        merchant_name: Optional[str] = None,
        payment_channel: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None
    ) -> Optional[Transaction]:
        """
        Update an existing transaction.

        Args:
            transaction_id (str): The ID of the transaction to update.
            name (Optional[str]): New name for the transaction.
            amount (Optional[float]): New amount for the transaction.
            date (Optional[str]): New date for the transaction.
            category (Optional[List[str]]): New categories for the transaction.
            pending (Optional[bool]): New pending status.
            merchant_name (Optional[str]): New merchant name.
            payment_channel (Optional[str]): New payment channel.
            location (Optional[Dict[str, Any]]): New location information.

        Returns:
            Optional[Transaction]: The updated transaction if found, None otherwise.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> transaction = TransactionFacade.update_transaction(
            ...     transaction_id="txn-123",
            ...     name="Updated Grocery Store",
            ...     amount=80.00
            ... )
            >>> if transaction:
            ...     print(f"Updated transaction: {transaction.name} - ${transaction.amount}")
            ... else:
            ...     print("Transaction not found")
            Updated transaction: Updated Grocery Store - $80.00
        """
        try:
            transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
            if not transaction:
                return None

            if name is not None:
                transaction.name = name
            if amount is not None:
                transaction.amount = amount
            if date is not None:
                transaction.date = date
            if category is not None:
                transaction.category = category
            if pending is not None:
                transaction.pending = pending
            if merchant_name is not None:
                transaction.merchant_name = merchant_name
            if payment_channel is not None:
                transaction.payment_channel = payment_channel
            if location is not None:
                transaction.location = location

            db.session.commit()
            return transaction
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_transaction(transaction_id: str) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id (str): The ID of the transaction to delete.

        Returns:
            bool: True if the transaction was deleted, False if it wasn't found.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> success = TransactionFacade.delete_transaction("txn-123")
            >>> print(f"Transaction deleted: {success}")
            Transaction deleted: True
        """
        try:
            transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
            if not transaction:
                return False

            db.session.delete(transaction)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def sync_transactions(account_id: str, transactions_data: List[Dict[str, Any]]) -> List[Transaction]:
        """
        Sync transactions from Plaid data.

        This method synchronizes transaction data received from Plaid with the local database.
        It handles both creating new transactions and updating existing ones.

        Args:
            account_id (str): The ID of the account whose transactions to sync.
            transactions_data (List[Dict[str, Any]]): List of transaction data from Plaid.

        Returns:
            List[Transaction]: List of synchronized transactions.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> plaid_data = [
            ...     {
            ...         "transaction_id": "txn-123",
            ...         "name": "Grocery Store",
            ...         "amount": 75.50,
            ...         "date": "2024-03-15",
            ...         "category": ["Food", "Groceries"],
            ...         "pending": False,
            ...         "merchant_name": "Whole Foods",
            ...         "payment_channel": "in store",
            ...         "location": {"city": "San Francisco", "state": "CA"}
            ...     }
            ... ]
            >>> transactions = TransactionFacade.sync_transactions("acc-123", plaid_data)
            >>> print(f"Synced {len(transactions)} transactions")
            Synced 1 transactions
        """
        try:
            synced_transactions = []
            for tx_data in transactions_data:
                # Check if transaction already exists
                existing_tx = Transaction.query.filter_by(
                    transaction_id=tx_data['transaction_id']
                ).first()

                if existing_tx:
                    # Update existing transaction
                    updated_tx = TransactionFacade.update_transaction(
                        transaction_id=tx_data['transaction_id'],
                        name=tx_data.get('name'),
                        amount=tx_data.get('amount'),
                        date=tx_data.get('date'),
                        category=tx_data.get('category'),
                        pending=tx_data.get('pending'),
                        merchant_name=tx_data.get('merchant_name'),
                        payment_channel=tx_data.get('payment_channel'),
                        location=tx_data.get('location')
                    )
                    if updated_tx:
                        synced_transactions.append(updated_tx)
                else:
                    # Create new transaction
                    new_tx = TransactionFacade.create_transaction(
                        transaction_id=tx_data['transaction_id'],
                        account_id=account_id,
                        name=tx_data['name'],
                        amount=tx_data['amount'],
                        date=tx_data['date'],
                        category=tx_data.get('category'),
                        pending=tx_data.get('pending', False),
                        merchant_name=tx_data.get('merchant_name'),
                        payment_channel=tx_data.get('payment_channel'),
                        location=tx_data.get('location')
                    )
                    synced_transactions.append(new_tx)

            return synced_transactions
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
