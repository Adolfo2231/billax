"""
Account Facade for managing bank account operations.

This module provides a facade class that handles business logic related to bank accounts.
It acts as an intermediary between the API layer and the database, managing:
- Account creation and updates
- Account retrieval and filtering
- Account synchronization with Plaid
- Database transaction management

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facade.account_facade import AccountFacade
    >>> # Create a new account
    >>> account = AccountFacade.create_account(
    ...     account_id="acc-123",
    ...     user_id="user-123",
    ...     name="Checking Account",
    ...     type="depository",
    ...     balance=1000.00
    ... )
    >>> print(f"Created account: {account.name}")
    Created account: Checking Account
"""

from app.models.bank_account import BankAccount
from app import db
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError

class AccountFacade:
    """
    Business logic layer for handling bank account operations.

    This class provides a simplified interface for managing bank accounts in the system.
    It handles all database operations related to accounts, including creation, updates,
    retrieval, and synchronization with external services like Plaid.

    Example:
        >>> # Get all accounts for a user
        >>> accounts = AccountFacade.get_accounts_by_user("user-123")
        >>> for account in accounts:
        ...     print(f"Account: {account.name} - Balance: ${account.balance}")
        Account: Checking - Balance: $1000.00
        Account: Savings - Balance: $5000.00
    """

    @staticmethod
    def get_all_accounts() -> List[BankAccount]:
        """
        Get all bank accounts from the database.

        Returns:
            List[BankAccount]: A list of all bank accounts in the system.

        Example:
            >>> accounts = AccountFacade.get_all_accounts()
            >>> print(f"Total accounts: {len(accounts)}")
            Total accounts: 50
        """
        return BankAccount.query.all()

    @staticmethod
    def get_account_by_id(account_id: str) -> Optional[BankAccount]:
        """
        Get a specific bank account by its ID.

        Args:
            account_id (str): The unique identifier of the account.

        Returns:
            Optional[BankAccount]: The bank account if found, None otherwise.

        Example:
            >>> account = AccountFacade.get_account_by_id("acc-123")
            >>> if account:
            ...     print(f"Found account: {account.name}")
            ... else:
            ...     print("Account not found")
            Found account: Checking Account
        """
        return BankAccount.query.filter_by(account_id=account_id).first()

    @staticmethod
    def get_accounts_by_user(user_id: str) -> List[BankAccount]:
        """
        Get all bank accounts for a specific user.

        Args:
            user_id (str): The ID of the user whose accounts to retrieve.

        Returns:
            List[BankAccount]: A list of bank accounts belonging to the user.

        Example:
            >>> accounts = AccountFacade.get_accounts_by_user("user-123")
            >>> print(f"User has {len(accounts)} accounts")
            User has 2 accounts
        """
        return BankAccount.query.filter_by(user_id=user_id).all()

    @staticmethod
    def create_account(
        account_id: str,
        user_id: str,
        name: str,
        type: str,
        balance: float,
        official_name: Optional[str] = None,
        subtype: Optional[str] = None,
        mask: Optional[str] = None
    ) -> BankAccount:
        """
        Create a new bank account.

        Args:
            account_id (str): The unique identifier for the account.
            user_id (str): The ID of the user who owns the account.
            name (str): The display name of the account.
            type (str): The type of account (e.g., 'depository', 'credit').
            balance (float): The current balance of the account.
            official_name (Optional[str]): The official name of the account.
            subtype (Optional[str]): The subtype of the account.
            mask (Optional[str]): The last 4 digits of the account number.

        Returns:
            BankAccount: The newly created bank account.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> account = AccountFacade.create_account(
            ...     account_id="acc-123",
            ...     user_id="user-123",
            ...     name="Checking Account",
            ...     type="depository",
            ...     balance=1000.00,
            ...     official_name="Personal Checking",
            ...     subtype="checking",
            ...     mask="1234"
            ... )
            >>> print(f"Created account: {account.name}")
            Created account: Checking Account
        """
        try:
            account = BankAccount(
                account_id=account_id,
                user_id=user_id,
                name=name,
                type=type,
                balance=balance,
                official_name=official_name,
                subtype=subtype,
                mask=mask
            )

            db.session.add(account)
            db.session.commit()
            return account
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_account(
        account_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        balance: Optional[float] = None,
        official_name: Optional[str] = None,
        subtype: Optional[str] = None,
        mask: Optional[str] = None
    ) -> Optional[BankAccount]:
        """
        Update an existing bank account.

        Args:
            account_id (str): The ID of the account to update.
            name (Optional[str]): New display name for the account.
            type (Optional[str]): New account type.
            balance (Optional[float]): New account balance.
            official_name (Optional[str]): New official name.
            subtype (Optional[str]): New account subtype.
            mask (Optional[str]): New account mask.

        Returns:
            Optional[BankAccount]: The updated bank account if found, None otherwise.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> account = AccountFacade.update_account(
            ...     account_id="acc-123",
            ...     name="New Checking Account",
            ...     balance=1500.00
            ... )
            >>> if account:
            ...     print(f"Updated account: {account.name} - New balance: ${account.balance}")
            ... else:
            ...     print("Account not found")
            Updated account: New Checking Account - New balance: $1500.00
        """
        try:
            account = BankAccount.query.filter_by(account_id=account_id).first()
            if not account:
                return None

            if name is not None:
                account.name = name
            if type is not None:
                account.type = type
            if balance is not None:
                account.balance = balance
            if official_name is not None:
                account.official_name = official_name
            if subtype is not None:
                account.subtype = subtype
            if mask is not None:
                account.mask = mask

            db.session.commit()
            return account
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_account(account_id: str) -> bool:
        """
        Delete a bank account.

        Args:
            account_id (str): The ID of the account to delete.

        Returns:
            bool: True if the account was deleted, False if it wasn't found.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> success = AccountFacade.delete_account("acc-123")
            >>> print(f"Account deleted: {success}")
            Account deleted: True
        """
        try:
            account = BankAccount.query.filter_by(account_id=account_id).first()
            if not account:
                return False

            db.session.delete(account)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def sync_accounts_from_plaid(user_id: str, accounts_data: List[Dict[str, Any]]) -> List[BankAccount]:
        """
        Sync bank accounts from Plaid data.

        This method synchronizes bank account data received from Plaid with the local database.
        It handles both creating new accounts and updating existing ones.

        Args:
            user_id (str): The ID of the user whose accounts to sync.
            accounts_data (List[Dict[str, Any]]): List of account data from Plaid.

        Returns:
            List[BankAccount]: List of synchronized bank accounts.

        Raises:
            SQLAlchemyError: If there's an error during database operations.

        Example:
            >>> plaid_data = [
            ...     {
            ...         "account_id": "acc-123",
            ...         "name": "Checking Account",
            ...         "type": "depository",
            ...         "balances": {"current": 1000.00},
            ...         "official_name": "Personal Checking",
            ...         "subtype": "checking",
            ...         "mask": "1234"
            ...     }
            ... ]
            >>> accounts = AccountFacade.sync_accounts_from_plaid("user-123", plaid_data)
            >>> print(f"Synced {len(accounts)} accounts")
            Synced 1 accounts
        """
        try:
            synced_accounts = []
            for acc_data in accounts_data:
                # Check if account already exists
                existing_acc = BankAccount.query.filter_by(
                    account_id=acc_data['account_id']
                ).first()

                if existing_acc:
                    # Update existing account
                    updated_acc = AccountFacade.update_account(
                        account_id=acc_data['account_id'],
                        name=acc_data.get('name'),
                        type=acc_data.get('type'),
                        balance=acc_data.get('balances', {}).get('current'),
                        official_name=acc_data.get('official_name'),
                        subtype=acc_data.get('subtype'),
                        mask=acc_data.get('mask')
                    )
                    if updated_acc:
                        synced_accounts.append(updated_acc)
                else:
                    # Create new account
                    new_acc = AccountFacade.create_account(
                        account_id=acc_data['account_id'],
                        user_id=user_id,
                        name=acc_data['name'],
                        type=acc_data['type'],
                        balance=acc_data['balances']['current'],
                        official_name=acc_data.get('official_name'),
                        subtype=acc_data.get('subtype'),
                        mask=acc_data.get('mask')
                    )
                    synced_accounts.append(new_acc)

            return synced_accounts
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
