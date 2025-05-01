"""
📦 Module: plaid_service.py
🔹 Description:
    This module handles all interactions with the Plaid API, including token creation,
    public token exchange, and retrieval of bank transaction data. It is used
    by the API layer to securely connect to user bank data in a sandbox or production environment.

🔹 Responsibilities:
    - Generate link tokens for Plaid Link integration
    - Exchange public tokens for access tokens
    - Create sandbox tokens for testing
    - Fetch recent transaction data from Plaid accounts
    - Fetch account data from Plaid

🔹 Usage:
    Typical usage:
        from app.services.plaid_service import (
            create_link_token,
            exchange_public_token,
            create_sandbox_public_token,
            get_transactions,
            get_accounts
        )

🔹 Environment:
    Requires the following environment variables:
        - PLAID_CLIENT_ID
        - PLAID_SECRET
        - PLAID_ENV

🔹 Dependencies:
    - plaid (Plaid Python SDK)
    - python-dotenv
    - datetime
"""

import os
import datetime
from datetime import timedelta
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
from plaid import ApiClient, Configuration, Environment
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
from app.exceptions.exceptions import APIConnectionError
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.transaction import Transaction
import plaid

# Load environment variables
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox").lower()

# Map environments
env_map = {
    "sandbox": Environment.Sandbox,
    "development": Environment.Sandbox,  # fallback to Sandbox for dev
    "production": Environment.Production
}
plaid_host = env_map.get(PLAID_ENV, Environment.Sandbox)

# Configure Plaid client
configuration = Configuration(
    host=plaid_host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


def create_link_token(user_id: str) -> str:
    """
    Creates a link_token to initialize the Plaid Link flow.

    This method generates a link token that is used to initialize the Plaid Link
    interface on the frontend. The token is specific to the user and includes
    configuration for the Plaid products being used.

    Args:
        user_id (str): Unique user ID from your system.

    Returns:
        str: A Plaid link token to send to the frontend.

    Raises:
        Exception: If there is an error creating the link token.

    Example:
        >>> token = create_link_token("user-123")
        >>> print(f"Generated link token: {token}")
        Generated link token: link-sandbox-1234567890
    """
    try:
        plaid_user = LinkTokenCreateRequestUser(client_user_id=user_id)
        request = LinkTokenCreateRequest(
            products=[Products('transactions')],
            client_name="Billax Finance",
            country_codes=[CountryCode('US')],
            language='en',
            user=plaid_user
        )
        response = client.link_token_create(request)
        return response.to_dict()["link_token"]
    except ApiException as e:
        print(f"[Plaid] Error creating link token: {e}")
        raise Exception("Error creating link token with Plaid")


def exchange_public_token(public_token: str) -> str:
    """
    Exchanges a public_token for a long-term access_token.

    This method takes a short-lived public token from Plaid Link and exchanges it
    for a permanent access token that can be used to access the user's financial data.

    Args:
        public_token (str): The short-lived token returned from Plaid Link.

    Returns:
        str: A permanent access_token to access user data.

    Raises:
        Exception: If there is an error exchanging the public token.

    Example:
        >>> access_token = exchange_public_token("public-sandbox-1234567890")
        >>> print(f"Generated access token: {access_token}")
        Generated access token: access-sandbox-1234567890
    """
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        return response.to_dict()["access_token"]
    except ApiException as e:
        print(f"[Plaid] Error exchanging public token: {e}")
        raise Exception("Error exchanging public token with Plaid")


def create_sandbox_public_token() -> Dict[str, str]:
    """
    Creates a public_token for testing in the sandbox environment.

    This method generates a public token for testing purposes in the Plaid sandbox
    environment. It uses a predefined test institution.

    Returns:
        Dict[str, str]: Sandbox public_token response from Plaid.

    Raises:
        Exception: If there is an error creating the sandbox public token.

    Example:
        >>> response = create_sandbox_public_token()
        >>> print(f"Sandbox public token: {response['public_token']}")
        Sandbox public token: public-sandbox-1234567890
    """
    try:
        request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",
            initial_products=[Products("transactions")]
        )
        response = client.sandbox_public_token_create(request)
        return response.to_dict()
    except ApiException as e:
        print(f"[Plaid] Error creating sandbox public token: {e}")
        raise Exception("Error creating sandbox public_token with Plaid")


def convert_dates(obj: Any) -> Any:
    """
    Recursively converts all datetime.date objects in a structure to ISO string format.

    This utility function is used to convert date objects to strings when preparing
    data for JSON serialization or API responses.

    Args:
        obj (Any): Dictionary, list, or primitive containing date values.

    Returns:
        Any: Structure with dates converted to strings.

    Example:
        >>> data = {
        ...     'date': datetime.date(2024, 3, 25),
        ...     'transactions': [
        ...         {'date': datetime.date(2024, 3, 24)}
        ...     ]
        ... }
        >>> converted = convert_dates(data)
        >>> print(converted['date'])
        2024-03-25
    """
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj


def get_transactions(access_token: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get transactions for a specific date range from Plaid.

    This method retrieves transaction data from Plaid for a given date range.
    It handles date conversion and error handling for the Plaid API call.

    Args:
        access_token (str): The Plaid access token.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        Dict[str, Any]: Transactions data from Plaid.

    Raises:
        APIConnectionError: If there is an error connecting to the Plaid API.

    Example:
        >>> transactions = get_transactions(
        ...     "access-sandbox-1234567890",
        ...     "2024-03-01",
        ...     "2024-03-31"
        ... )
        >>> print(f"Retrieved {len(transactions['transactions'])} transactions")
        Retrieved 50 transactions
    """
    try:
        # Convert string dates to date objects
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date_obj,
            end_date=end_date_obj,
            options=TransactionsGetRequestOptions(
                count=500,
                offset=0
            )
        )
        response = client.transactions_get(request)
        return response.to_dict()
    except plaid.ApiException as e:
        raise APIConnectionError("Plaid", str(e))


def sync_transactions(user_id: str, start_date: str, end_date: str) -> List[Transaction]:
    """
    Sync transactions for a user's accounts with the local database.

    This method retrieves transactions from Plaid for a given date range and
    synchronizes them with the local database. It handles both new transactions
    and updates to existing ones.

    Args:
        user_id (str): The user ID.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        List[Transaction]: List of synced transactions.

    Raises:
        ValueError: If the user is not found or not connected to Plaid.
        APIConnectionError: If there is an error connecting to the Plaid API.

    Example:
        >>> transactions = sync_transactions(
        ...     "user-123",
        ...     "2024-03-01",
        ...     "2024-03-31"
        ... )
        >>> print(f"Synced {len(transactions)} transactions")
        Synced 50 transactions
    """
    try:
        # Get user's access token
        user = UserRepository().get_by_id(user_id)
        if not user or not user.plaid_access_token:
            raise ValueError("User not found or not connected to Plaid")
            
        # Get transactions from Plaid
        response = get_transactions(user.plaid_access_token, start_date, end_date)
        
        # Process and save transactions
        transactions = []
        for tx in response.get('transactions', []):
            # Check if transaction already exists
            existing_tx = TransactionRepository().get_by_transaction_id(tx['transaction_id'])
            
            if existing_tx:
                # Update existing transaction
                existing_tx.amount = tx['amount']
                existing_tx.date = tx['date']
                existing_tx.name = tx['name']
                existing_tx.merchant_name = tx.get('merchant_name')
                existing_tx.category = tx.get('category', [])
                existing_tx.pending = tx.get('pending', False)
                TransactionRepository().save(existing_tx)
                transactions.append(existing_tx)
            else:
                # Create new transaction
                new_tx = Transaction(
                    transaction_id=tx['transaction_id'],
                    account_id=tx['account_id'],
                    amount=tx['amount'],
                    date=tx['date'],
                    name=tx['name'],
                    merchant_name=tx.get('merchant_name'),
                    category=tx.get('category', []),
                    pending=tx.get('pending', False)
                )
                TransactionRepository().save(new_tx)
                transactions.append(new_tx)
                
        return transactions
    except Exception as e:
        print(f"[Plaid] Error syncing transactions: {e}")
        raise


def get_accounts(access_token: str) -> Dict[str, Any]:
    """
    Get account information from Plaid.

    This method retrieves account data from Plaid for a given access token.
    It includes information about balances, account types, and other metadata.

    Args:
        access_token (str): The Plaid access token.

    Returns:
        Dict[str, Any]: Account data from Plaid.

    Raises:
        APIConnectionError: If there is an error connecting to the Plaid API.

    Example:
        >>> accounts = get_accounts("access-sandbox-1234567890")
        >>> print(f"Retrieved {len(accounts['accounts'])} accounts")
        Retrieved 3 accounts
    """
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        return response.to_dict()
    except plaid.ApiException as e:
        raise APIConnectionError("Plaid", str(e))
