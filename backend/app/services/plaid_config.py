import os
from typing import Dict, Any, List
import datetime
from datetime import timedelta
from dotenv import load_dotenv
from plaid import ApiClient, Configuration, Environment
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException
from app.utils.plaid_exceptions import PlaidTokenError, PlaidDataSyncError
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest

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

def create_link_plaid(user_id: str) -> Dict[str, Any]:
    """
    Creates a link_token to initialize the Plaid Link flow.

    Args:
        user_id (str): Unique user ID from your system.

    Returns:
        Dict[str, Any]: {
            'link_token': str,
            'expiration': str (ISO format),
            'request_id': dict
        }

    Raises:
        PlaidTokenError: If the link token cannot be created.

    Example:
        >>> response = create_link_plaid("user123")
        >>> print(f"Link token: {response['link_token']}")
        Link token: link-sandbox-1234567890
    """
    try:
        user = LinkTokenCreateRequestUser(client_user_id=str(user_id))
        
        request = LinkTokenCreateRequest(
            products=[
                Products('transactions'),
                Products('identity'),
                Products('investments'),
                Products('liabilities')
            ],
            client_name="Billax Finance",
            country_codes=[CountryCode('US')],
            language='en',
            user=user
        )

        response = client.link_token_create(request)
        response_dict = response.to_dict()

        if 'link_token' not in response_dict:
            raise PlaidTokenError("No link_token in response")

        return {
            "link_token": response_dict["link_token"],
            "expiration": (datetime.datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "request_id": request.to_dict()
        }

    except ApiException as e:
        raise PlaidTokenError(f"Failed to create link token: {str(e)}")
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

def convert_dates(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts datetime objects to string format in a list of dictionaries.
    
    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing data with dates.
        
    Returns:
        List[Dict[str, Any]]: List with dates converted to ISO format strings.
    """
    for item in data:
        for key, value in item.items():
            if isinstance(value, datetime.datetime):
                item[key] = value.isoformat()
            elif isinstance(value, dict):
                convert_dates([value])
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