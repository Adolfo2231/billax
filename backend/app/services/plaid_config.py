import os
from typing import Dict, Any
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
from app.utils.plaid_exceptions import PlaidTokenError

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
            'expiration': str (ISO format)
        }

    Raises:
        PlaidTokenError: If the link token cannot be created.
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
