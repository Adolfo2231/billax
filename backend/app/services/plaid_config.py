import os
from typing import Dict, Any, List
import datetime
from datetime import timedelta
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from app.utils.plaid_exceptions import PlaidTokenError, PlaidDataSyncError
from app.repositories.user_repository import UserRepository
from app.utils.plaid_exceptions import PlaidDataSyncError, PlaidUserNotLinkedError, UserNotFoundError

# Load environment variables
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox").lower()

# Create Plaid client (simplified for now)
client = plaid_api.PlaidApi()

def create_link_plaid(user_id: str) -> Dict[str, Any]:
    """
    Creates a link_token to initialize the Plaid Link flow.
    Simplified version for Railway deployment.
    """
    try:
        # For now, return a mock response to allow the app to start
        # This will be properly implemented once we have the correct Plaid setup
        return {
            "link_token": "mock-link-token-for-development",
            "message": "Plaid integration pending proper configuration"
        }
    except Exception as e:
        raise PlaidTokenError(f"Unexpected error creating link token: {str(e)}")

def plaid_public_token() -> Dict[str, Any]:
    """
    Creates a public_token for testing in the sandbox environment.

    This method generates a public token for testing purposes in the Plaid sandbox
    environment. It uses a predefined test institution.

    Returns:
        Dict[str, Any]: {
            'public_token': str,
            'expiration': str (ISO format),
            'request_id': dict
        }

    Raises:
        PlaidTokenError: If there is an error creating the sandbox public token.

    Example:
        >>> response = plaid_public_token()
        >>> print(f"Sandbox public token: {response['public_token']}")
        Sandbox public token: public-sandbox-1234567890
    """
    try:
        request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",
            initial_products=[Products("transactions")]
        )
        response = client.sandbox_public_token_create(request)
        response_dict = response.to_dict()

        if 'public_token' not in response_dict:
            raise PlaidTokenError("No public_token in response")

        return {
            "public_token": response_dict["public_token"],
            "expiration": (datetime.datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "request_id": request.to_dict()
        }
    except ApiException as e:
        raise PlaidTokenError(f"Failed to create sandbox public token: {str(e)}")
    except Exception as e:
        raise PlaidTokenError(f"Unexpected error creating sandbox public token: {str(e)}")
    
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
        PlaidTokenError: If there is an error exchanging the public token.

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
        raise PlaidTokenError(f"Failed to exchange public token: {str(e)}")

def convert_dates(data):
    """
    Recursivamente convierte objetos datetime y date a string en cualquier estructura.
    """
    if isinstance(data, dict):
        return {k: convert_dates(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates(item) for item in data]
    elif isinstance(data, (datetime.datetime, datetime.date)):
        return data.isoformat()
    else:
        return data

def sync_accounts(access_token: str) -> List[Dict[str, Any]]:
    """
    Retrieves account information from Plaid.

    Args:
        access_token (str): The Plaid access token for the user.

    Returns:
        List[Dict[str, Any]]: List of account information.

    Raises:
        PlaidDataSyncError: If there is an error retrieving accounts.

    Example:
        >>> accounts = get_accounts("access-sandbox-1234567890")
        >>> for account in accounts:
        ...     print(f"Account: {account['name']} - Balance: ${account['balances']['current']}")
        Account: Checking - Balance: $1000.00
        Account: Savings - Balance: $5000.00
    """
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        result = response.to_dict()
        
        # Extract accounts from response
        accounts = result.get('accounts', [])
        
        # Convert all dates to string format
        return convert_dates(accounts)
        
    except ApiException as e:
        raise PlaidDataSyncError(f"Failed to retrieve accounts: {str(e)}")

def get_transactions(access_token: str, start_date: str = None, end_date: str = None, count: int = None) -> Dict[str, Any]:
    """
    Retrieves transaction information from Plaid.

    Args:
        access_token (str): The Plaid access token for the user.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        count (int): Number of transactions to retrieve (optional, if not specified gets all).

    Returns:
        Dict[str, Any]: Dictionary containing transactions and other metadata.

    Raises:
        PlaidDataSyncError: If there is an error retrieving transactions.

    Example:
        >>> transactions = get_transactions("access-sandbox-1234567890", "2024-03-01", "2024-03-31", 100)
        >>> print(f"Retrieved {len(transactions['transactions'])} transactions")
        Retrieved 100 transactions
    """
    try:
        # Si no hay fechas, usar los últimos 90 días
        if not end_date:
            end_date_obj = datetime.date.today()
        else:
            end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        if not start_date:
            # Por defecto, últimos 90 días
            start_date_obj = end_date_obj - datetime.timedelta(days=90)
        else:
            start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        
        all_transactions = []
        has_more = True
        offset = 0
        
        # Usar paginación para obtener todas las transacciones en el rango
        while has_more:
            # Si se especifica count, limitar la cantidad por request
            request_count = 100  # Plaid max is 100 per request
            if count is not None:
                remaining = count - len(all_transactions)
                if remaining <= 0:
                    break
                request_count = min(100, remaining)
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date_obj,
                end_date=end_date_obj,
                options={
                    'count': request_count,
                    'offset': offset
                }
            )
            response = client.transactions_get(request)
            result = response.to_dict()
            
            transactions = result.get('transactions', [])
            all_transactions.extend(transactions)
            
            has_more = result.get('has_more', False)
            offset += len(transactions)
            
            # Si no hay más transacciones, parar
            if not has_more:
                break
        
        # Si se especifica count, limitar a esa cantidad
        if count is not None:
            all_transactions = all_transactions[:count]
        
        # Ordenar por fecha (más recientes primero)
        all_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        result = {
            'accounts': result.get('accounts', []),
            'transactions': all_transactions,
            'total_transactions': len(all_transactions),
            'has_more': has_more,
            'request_id': result.get('request_id')
        }
        
        return convert_dates(result)
    except ApiException as e:
        raise PlaidDataSyncError(f"Failed to retrieve transactions: {str(e)}")

def sync_transactions(user_id: str, start_date: str, end_date: str, count: int = None) -> Dict[str, Any]:
    """
    Retrieves transaction information from Plaid for a user.

    This method gets the user's access token and retrieves transactions from Plaid
    for the specified date range. It does not perform any database operations.

    Args:
        user_id (str): The user ID.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        count (int): Number of transactions to retrieve (optional, if not specified gets all).

    Returns:
        Dict[str, Any]: Dictionary containing transactions and other metadata from Plaid.

    Raises:
        UserNotFoundError: If the user is not found.
        PlaidUserNotLinkedError: If the user is not connected to Plaid.
        PlaidDataSyncError: If there is an error retrieving transaction data.

    Example:
        >>> transactions = sync_transactions(
        ...     "user-123",
        ...     "2024-03-01",
        ...     "2024-03-31"
        ... )
        >>> print(f"Retrieved {len(transactions['transactions'])} transactions")
        Retrieved 50 transactions
    """
    try:
        # Get user's access token
        user = UserRepository().get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        if not user.plaid_access_token:
            raise PlaidUserNotLinkedError()
            
        # Get transactions from Plaid
        return get_transactions(user.plaid_access_token, start_date, end_date, count)
        
    except (UserNotFoundError, PlaidUserNotLinkedError, PlaidDataSyncError):
        # Re-raise our domain exceptions
        raise
    except Exception as e:
        raise PlaidDataSyncError(f"Failed to retrieve transactions: {str(e)}")