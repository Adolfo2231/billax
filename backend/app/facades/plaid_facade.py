"""
Plaid Facade for managing financial data integration.

This module provides a facade class that handles business logic related to Plaid integration.
It acts as an intermediary between the API layer and the Plaid service, managing:
- Token exchange and management
- Account linking and synchronization
- Transaction synchronization
- Error handling and data persistence

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facades.plaid_facade import PlaidFacade
    >>> facade = PlaidFacade()
    >>> # Create link token for user
    >>> link_token = facade.create_link_token("user-123")
    >>> print(f"Link token: {link_token}")
    Link token: link-sandbox-1234567890
"""

import os
from typing import List, Optional
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.exceptions import ApiException

from app.extensions import db
from app.facade.user_facade import UserFacade
from app.exceptions import APIConnectionError
from app.services import plaid_service
from app.models.bank_account import BankAccount
from app.repositories.bank_account_repository import BankAccountRepository


class PlaidFacade:
    """
    Facade class for managing Plaid integration and related business logic.

    This class provides a simplified interface for interacting with Plaid's API
    and managing the associated business logic. It handles token management,
    account linking, and data synchronization while abstracting away the
    complexity of the underlying services.

    Example:
        >>> facade = PlaidFacade()
        >>> # Create link token for user
        >>> link_token = facade.create_link_token("user-123")
        >>> print(f"Link token: {link_token}")
        Link token: link-sandbox-1234567890
    """

    @staticmethod
    def create_link_token(user_id: str) -> str:
        """
        Creates a link token for Plaid Link initialization.

        This method generates a link token that is used to initialize the Plaid Link
        interface on the frontend. It configures the Plaid client and creates a token
        with the appropriate permissions and settings.

        Args:
            user_id (str): The ID of the user to create the link token for.

        Returns:
            str: The link token from Plaid.

        Raises:
            ValueError: If the user is not found.
            APIConnectionError: If there's an error connecting to Plaid.

        Example:
            >>> token = PlaidFacade.create_link_token("user-123")
            >>> print(f"Generated link token: {token}")
            Generated link token: link-sandbox-1234567890
        """
        try:
            user = UserFacade.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Configure Plaid client
            client_config = plaid.Configuration(
                host=plaid.Environment.Sandbox,
                api_key={
                    'clientId': os.getenv('PLAID_CLIENT_ID'),
                    'secret': os.getenv('PLAID_SECRET'),
                }
            )
            api_client = plaid.ApiClient(client_config)
            client = plaid_api.PlaidApi(api_client)

            # Create link token request
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(user_id)
                ),
                client_name="Billax Finance",
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en"
            )

            # Create link token
            response = client.link_token_create(request)
            return response.link_token

        except plaid.ApiException as e:
            raise APIConnectionError("Plaid", str(e))

    @staticmethod
    def link_user_to_plaid(user_id: str, public_token: str) -> None:
        """
        Exchanges a public token for an access token and saves it to the user.

        This method handles the process of linking a user's bank account to Plaid.
        It exchanges the short-lived public token for a permanent access token
        and saves it to the user's record.

        Args:
            user_id (str): The ID of the user to link.
            public_token (str): The public token from Plaid Link.

        Raises:
            ValueError: If the user is not found.
            APIConnectionError: If there's an error connecting to Plaid.

        Example:
            >>> PlaidFacade.link_user_to_plaid(
            ...     "user-123",
            ...     "public-sandbox-1234567890"
            ... )
            >>> user = UserFacade.get_user_by_id("user-123")
            >>> print(f"User linked to Plaid: {bool(user.plaid_access_token)}")
            User linked to Plaid: True
        """
        try:
            user = UserFacade.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Configure Plaid client
            client_config = plaid.Configuration(
                host=plaid.Environment.Sandbox,
                api_key={
                    'clientId': os.getenv('PLAID_CLIENT_ID'),
                    'secret': os.getenv('PLAID_SECRET'),
                }
            )
            api_client = plaid.ApiClient(client_config)
            client = plaid_api.PlaidApi(api_client)

            # Exchange public token for access token
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            response = client.item_public_token_exchange(exchange_request)

            # Save access token to user
            user.plaid_access_token = response.access_token
            db.session.commit()

        except plaid.ApiException as e:
            raise APIConnectionError("Plaid", str(e))

    @staticmethod
    def sync_accounts_for_user(user_id: str) -> List[BankAccount]:
        """
        Fetches account data from Plaid and saves it in the database.

        This method retrieves the user's bank account information from Plaid
        and synchronizes it with the local database. It handles both new accounts
        and updates to existing ones.

        Args:
            user_id (str): The user whose accounts to sync.

        Returns:
            List[BankAccount]: List of saved account objects.

        Raises:
            ValueError: If the user is not found or not connected to Plaid.
            APIConnectionError: If there's an error connecting to Plaid.

        Example:
            >>> accounts = PlaidFacade.sync_accounts_for_user("user-123")
            >>> for account in accounts:
            ...     print(f"Account: {account.name} - Balance: ${account.current_balance}")
            Account: Checking - Balance: $1000.00
            Account: Savings - Balance: $5000.00
        """
        try:
            user = UserFacade.get_user_by_id(user_id)
            if not user or not user.plaid_access_token:
                raise ValueError("User not found or not connected to Plaid.")

            plaid_data = plaid_service.get_accounts(user.plaid_access_token)
            accounts_data = plaid_data.get("accounts", [])
            saved_accounts = []

            for acc in accounts_data:
                # Check if account already exists
                existing_account = BankAccountRepository().get_by_account_id(acc["account_id"])
                if existing_account:
                    # Update existing account
                    existing_account.name = acc["name"]
                    existing_account.official_name = acc.get("official_name")
                    existing_account.type = acc["type"]
                    existing_account.subtype = acc["subtype"]
                    existing_account.current_balance = acc["balances"]["current"]
                    existing_account.available_balance = acc["balances"].get("available")
                    existing_account.mask = acc.get("mask")
                    BankAccountRepository().save(existing_account)
                    saved_accounts.append(existing_account)
                else:
                    # Create new account
                    account = BankAccount(
                        user_id=user.id,
                        account_id=acc["account_id"],
                        name=acc["name"],
                        official_name=acc.get("official_name"),
                        type=acc["type"],
                        subtype=acc["subtype"],
                        current_balance=acc["balances"]["current"],
                        available_balance=acc["balances"].get("available"),
                        mask=acc.get("mask"),
                    )
                    BankAccountRepository().save(account)
                    saved_accounts.append(account)

            return saved_accounts

        except Exception as e:
            raise APIConnectionError("Plaid", str(e))

    @classmethod
    def sync_transactions(cls, user_id: str, start_date: str, end_date: str) -> List[Transaction]:
        """
        Sync transactions for a user's accounts.

        This method synchronizes transactions from Plaid for a given date range.
        It delegates the actual synchronization to the Plaid service while providing
        a clean interface for the API layer.

        Args:
            user_id (str): The user ID.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            List[Transaction]: List of synced transactions.

        Example:
            >>> transactions = PlaidFacade.sync_transactions(
            ...     "user-123",
            ...     "2024-03-01",
            ...     "2024-03-31"
            ... )
            >>> print(f"Synced {len(transactions)} transactions")
            Synced 50 transactions
        """
        from app.services.plaid_service import sync_transactions
        return sync_transactions(user_id, start_date, end_date) 