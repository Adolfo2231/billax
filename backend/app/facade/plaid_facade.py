"""
Plaid Facade for managing financial data integration.

This module provides a facade class that handles business logic related to Plaid integration.
It acts as an intermediary between the API layer and the Plaid service, managing:
- Token exchange and management
- Account synchronization
- Transaction synchronization
- Integration with other facades (User, Account, Transaction)

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facade.plaid_facade import PlaidFacade
    >>> # Link user to Plaid
    >>> PlaidFacade.link_user_to_plaid("user-123", "public-sandbox-1234567890")
    >>> # Sync accounts
    >>> accounts = PlaidFacade.sync_accounts_for_user("user-123")
    >>> print(f"Synced {len(accounts)} accounts")
    Synced 2 accounts
"""

from app.facades.user_facade import UserFacade
from app.facades.account_facade import AccountFacade
from app.facades.transaction_facade import TransactionFacade
from app.services import plaid_service
from typing import List, Dict, Any

class PlaidFacade:
    """
    Business logic layer for handling Plaid integration.

    This class provides a simplified interface for interacting with Plaid's API
    and managing the associated business logic. It coordinates with other facades
    (User, Account, Transaction) to provide a complete integration solution.

    Example:
        >>> # Link user to Plaid
        >>> PlaidFacade.link_user_to_plaid("user-123", "public-sandbox-1234567890")
        >>> # Sync accounts and transactions
        >>> accounts = PlaidFacade.sync_accounts_for_user("user-123")
        >>> transactions = PlaidFacade.sync_transactions_for_user("user-123")
    """

    @staticmethod
    def link_user_to_plaid(user_id: str, public_token: str) -> None:
        """
        Exchanges a public token for an access token and saves it to the user.

        This method handles the process of linking a user's bank account to Plaid.
        It exchanges the short-lived public token for a permanent access token
        and updates the user's record with the new token.

        Args:
            user_id (str): The authenticated user's ID.
            public_token (str): The token received from Plaid Link.

        Raises:
            Exception: If token exchange or update fails.

        Example:
            >>> PlaidFacade.link_user_to_plaid(
            ...     "user-123",
            ...     "public-sandbox-1234567890"
            ... )
            >>> user = UserFacade.get_user_by_id("user-123")
            >>> print(f"User linked to Plaid: {bool(user.plaid_access_token)}")
            User linked to Plaid: True
        """
        access_token = plaid_service.exchange_public_token(public_token)
        UserFacade.update_plaid_access_token(user_id, access_token)

    @staticmethod
    def sync_accounts_for_user(user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches account data from Plaid and saves it in the database.

        This method retrieves the user's bank account information from Plaid
        and synchronizes it with the local database. It delegates the actual
        account creation/update to the AccountFacade.

        Args:
            user_id (str): The user whose accounts to sync.

        Returns:
            List[Dict[str, Any]]: List of saved account data.

        Raises:
            ValueError: If the user is not found or not connected to Plaid.

        Example:
            >>> accounts = PlaidFacade.sync_accounts_for_user("user-123")
            >>> for account in accounts:
            ...     print(f"Account: {account['name']} - Balance: ${account['current_balance']}")
            Account: Checking - Balance: $1000.00
            Account: Savings - Balance: $5000.00
        """
        user = UserFacade.get_user_by_id(user_id)
        if not user or not user.plaid_access_token:
            raise ValueError("User not found or not connected to Plaid.")

        plaid_data = plaid_service.get_accounts(user.plaid_access_token)
        accounts_data = plaid_data.get("accounts", [])
        
        # Use AccountFacade to handle the synchronization
        synced_accounts = AccountFacade.sync_accounts_from_plaid(user_id, accounts_data)
        
        return [account.to_dict() for account in synced_accounts]

    @staticmethod
    def sync_transactions_for_user(user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches transaction data from Plaid and saves it in the database.

        This method retrieves transactions for all of the user's accounts from Plaid
        and synchronizes them with the local database. It delegates the actual
        transaction creation/update to the TransactionFacade.

        Args:
            user_id (str): The user whose transactions to sync.

        Returns:
            List[Dict[str, Any]]: List of saved transaction data.

        Raises:
            ValueError: If the user is not found or not connected to Plaid.

        Example:
            >>> transactions = PlaidFacade.sync_transactions_for_user("user-123")
            >>> print(f"Synced {len(transactions)} transactions")
            Synced 50 transactions
            >>> # View some transaction details
            >>> for tx in transactions[:2]:
            ...     print(f"{tx['date']}: {tx['name']} - ${tx['amount']}")
            2024-03-15: Grocery Store - $75.50
            2024-03-14: Gas Station - $45.25
        """
        user = UserFacade.get_user_by_id(user_id)
        if not user or not user.plaid_access_token:
            raise ValueError("User not found or not connected to Plaid.")

        # Get all user's accounts
        accounts = AccountFacade.get_accounts_by_user(user_id)
        all_synced_transactions = []

        for account in accounts:
            # Get transactions for each account
            plaid_data = plaid_service.get_transactions(
                user.plaid_access_token,
                account.account_id
            )
            transactions_data = plaid_data.get("transactions", [])
            
            # Use TransactionFacade to handle the synchronization
            synced_transactions = TransactionFacade.sync_transactions(
                account.account_id,
                transactions_data
            )
            
            all_synced_transactions.extend([tx.to_dict() for tx in synced_transactions])

        return all_synced_transactions
