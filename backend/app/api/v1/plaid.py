"""
Plaid Integration API endpoints for financial data management.

This module provides REST API endpoints for interacting with the Plaid API,
enabling secure access to financial data through a standardized interface.
It handles operations such as token creation, account linking, and transaction
synchronization, with proper JWT token validation and error handling.

Key Features:
- Link token generation for Plaid Link integration
- Public token exchange for access tokens
- Sandbox token creation for testing
- Account and transaction synchronization
- Secure token management and validation

Example:
    >>> # Create a link token for Plaid Link
    >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
    >>> response = client.post('/api/v1/plaid/create_link_token', headers=headers)
    >>> print(response.status_code)
    200
    >>> print(response.json['link_token'])
    link-sandbox-1234567890
"""

from typing import Dict, Any, Tuple, List
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from app.services.plaid_service import (
    create_link_token,
    exchange_public_token,
    create_sandbox_public_token,
    get_transactions
)
from app.facades.plaid_facade import PlaidFacade
from app.exceptions.exceptions import APIConnectionError
from app.decorators import token_required

# Create the Plaid namespace
plaid_ns = Namespace('plaid', description='Plaid integration operations')

# Swagger Models for request/response documentation
link_token_response = plaid_ns.model('LinkTokenResponse', {
    'link_token': fields.String(description='Token to initialize Plaid Link')
})

access_token_response = plaid_ns.model('AccessTokenResponse', {
    'access_token': fields.String(description='Permanent token to access Plaid data')
})

sandbox_token_response = plaid_ns.model('SandboxTokenResponse', {
    'public_token': fields.String(description='Public token for sandbox'),
    'request_id': fields.String(description='Request ID from Plaid')
})

transactions_model = plaid_ns.model('Transaction', {
    'transaction_id': fields.String,
    'name': fields.String,
    'amount': fields.Float,
    'date': fields.String,
})

transactions_response = plaid_ns.model('TransactionsResponse', {
    'transactions': fields.List(fields.Nested(transactions_model))
})

link_request = plaid_ns.model("PlaidLink", {
    "public_token": fields.String(required=True, description="Public token from Plaid Link")
})

account_model = plaid_ns.model('Account', {
    'account_id': fields.String(description='The Plaid account ID'),
    'name': fields.String(description='The account name'),
    'official_name': fields.String(description='The official account name'),
    'type': fields.String(description='The account type'),
    'subtype': fields.String(description='The account subtype'),
    'current_balance': fields.Float(description='The current balance'),
    'available_balance': fields.Float(description='The available balance'),
    'mask': fields.String(description='The last 4 digits of the account number')
})

accounts_response = plaid_ns.model('AccountsResponse', {
    'accounts': fields.List(fields.Nested(account_model))
})

# Models for documentation
link_token_model = plaid_ns.model('LinkToken', {
    'link_token': fields.String(description='Token to initialize Plaid Link')
})

public_token_model = plaid_ns.model('PublicToken', {
    'public_token': fields.String(description='Public token from Plaid Link'),
    'request_id': fields.String(description='Plaid request ID')
})


@plaid_ns.route('/create_link_token')
class CreateLinkToken(Resource):
    """
    Resource for creating Plaid Link tokens.

    This endpoint generates a link token that is used to initialize the Plaid Link
    interface for connecting bank accounts. The token is specific to the user and
    includes necessary configuration for the Plaid Link flow.
    """

    @plaid_ns.doc('create_link_token')
    @plaid_ns.marshal_with(link_token_model)
    @token_required
    def post(self, current_user) -> Dict[str, str]:
        """
        Create a link token for Plaid Link initialization.

        This endpoint generates a unique link token that is used to initialize
        the Plaid Link interface. The token includes user-specific configuration
        and is required to start the account linking process.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Dict[str, str]: Response containing:
                - link_token (str): Token to initialize Plaid Link

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.post('/api/v1/plaid/create_link_token', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['link_token'])
            link-sandbox-1234567890
        """
        link_token = PlaidFacade.create_link_token(current_user.id)
        return {'link_token': link_token}


@plaid_ns.route('/link')
class LinkAccount(Resource):
    """
    Resource for linking Plaid accounts.

    This endpoint handles the exchange of a public token for a permanent access token
    and links the user's bank accounts to their profile. It's called after the user
    successfully completes the Plaid Link flow.
    """

    @plaid_ns.doc('link_account')
    @plaid_ns.expect(plaid_ns.model('LinkRequest', {
        'public_token': fields.String(required=True, description='Public token from Plaid Link')
    }))
    @token_required
    def post(self, current_user) -> Dict[str, str]:
        """
        Exchange public token for access token and link account.

        This endpoint completes the Plaid account linking process by exchanging
        the temporary public token for a permanent access token and linking the
        user's bank accounts to their profile.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            Request body (JSON):
                - public_token (str): Public token received from Plaid Link

        Returns:
            Dict[str, str]: Response containing:
                - message (str): Success message

        Raises:
            HTTP 400: If public token is invalid
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> data = {'public_token': 'public-sandbox-1234567890'}
            >>> response = client.post('/api/v1/plaid/link', json=data, headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['message'])
            Accounts linked successfully
        """
        public_token = plaid_ns.payload['public_token']
        PlaidFacade.link_user_to_plaid(current_user.id, public_token)
        return {'message': 'Accounts linked successfully'}


@plaid_ns.route('/sandbox_public_token')
class CreateSandboxToken(Resource):
    """
    Resource for creating sandbox tokens.

    This endpoint generates a public token for testing purposes in the Plaid
    sandbox environment. It's used during development and testing to simulate
    the account linking process.
    """

    @plaid_ns.doc('create_sandbox_token')
    @plaid_ns.marshal_with(public_token_model)
    @token_required
    def post(self, current_user) -> Dict[str, str]:
        """
        Create a sandbox public token for testing.

        This endpoint generates a public token that can be used in the Plaid
        sandbox environment for testing the account linking process.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Dict[str, str]: Response containing:
                - public_token (str): Public token for sandbox
                - request_id (str): Plaid request ID

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.post('/api/v1/plaid/sandbox_public_token', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['public_token'])
            public-sandbox-1234567890
        """
        return PlaidFacade.create_sandbox_public_token()


@plaid_ns.route('/sync')
class SyncAccounts(Resource):
    """
    Resource for synchronizing Plaid accounts.

    This endpoint triggers a synchronization of the user's linked bank accounts
    with Plaid, updating account balances and other information.
    """

    @plaid_ns.doc('sync_accounts')
    @token_required
    def post(self, current_user) -> Dict[str, str]:
        """
        Sync accounts with Plaid.

        This endpoint synchronizes the user's linked bank accounts with Plaid,
        updating account balances and other information in the database.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Dict[str, str]: Response containing:
                - message (str): Success message with number of synced accounts

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.post('/api/v1/plaid/sync', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['message'])
            Successfully synced 3 accounts
        """
        accounts = PlaidFacade.sync_accounts_for_user(current_user.id)
        return {'message': f'Successfully synced {len(accounts)} accounts'}


@plaid_ns.route('/exchange_public_token/<string:public_token>')
class ExchangePublicToken(Resource):
    """
    Resource for exchanging public tokens.

    This endpoint exchanges a temporary public token for a permanent access token
    that can be used to access the user's financial data through the Plaid API.
    """

    @plaid_ns.doc(description="Exchange a public_token for a permanent access_token.")
    @plaid_ns.marshal_with(access_token_response)
    def post(self, public_token: str) -> Dict[str, str]:
        """
        Exchange public_token for access_token.

        This endpoint exchanges a temporary public token received from Plaid Link
        for a permanent access token that can be used to access the user's
        financial data.

        Args:
            public_token (str): The public token to exchange

        Returns:
            Dict[str, str]: Response containing:
                - access_token (str): Permanent access token

        Raises:
            HTTP 400: If public token is invalid
            HTTP 500: For server errors

        Example:
            >>> response = client.post('/api/v1/plaid/exchange_public_token/public-sandbox-1234567890')
            >>> print(response.status_code)
            200
            >>> print(response.json['access_token'])
            access-sandbox-1234567890
        """
        return {'access_token': exchange_public_token(public_token)}


@plaid_ns.route('/transactions/<string:access_token>')
class Transactions(Resource):
    """
    Resource for fetching transactions.

    This endpoint retrieves recent transactions for a given access token,
    providing access to the user's transaction history through the Plaid API.
    """

    @plaid_ns.doc(description="Fetch recent transactions for a given access_token.")
    @plaid_ns.marshal_with(transactions_response)
    def post(self, access_token: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get latest transactions from Plaid.

        This endpoint retrieves the most recent transactions for a given access token,
        providing access to the user's transaction history.

        Args:
            access_token (str): The access token for the account

        Returns:
            Dict[str, List[Dict[str, Any]]]: Response containing:
                - transactions (list): List of transaction objects
                    - transaction_id (str): Unique transaction ID
                    - name (str): Transaction name/description
                    - amount (float): Transaction amount
                    - date (str): Transaction date

        Raises:
            HTTP 400: If access token is invalid
            HTTP 500: For server errors

        Example:
            >>> response = client.post('/api/v1/plaid/transactions/access-sandbox-1234567890')
            >>> print(response.status_code)
            200
            >>> print(response.json['transactions'][0])
            {
                'transaction_id': '1234567890',
                'name': 'Grocery Store',
                'amount': 50.00,
                'date': '2024-01-01'
            }
        """
        return get_transactions(access_token)


@plaid_ns.route('/accounts')
class PlaidAccounts(Resource):
    """
    Resource for managing Plaid accounts.

    This endpoint provides access to the user's linked bank accounts,
    including account details and balances.
    """

    @plaid_ns.doc(security="Bearer")
    @plaid_ns.response(200, "Accounts retrieved successfully", accounts_response)
    @plaid_ns.response(401, "Unauthorized")
    @plaid_ns.response(500, "Error retrieving accounts")
    @jwt_required()
    def get(self) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        """
        Retrieves the user's linked bank accounts.

        This endpoint returns detailed information about all bank accounts
        linked to the user's profile, including balances and account details.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Tuple[Dict[str, List[Dict[str, Any]]], int]: Response containing:
                - accounts (list): List of account objects
                    - account_id (str): Plaid account ID
                    - name (str): Account name
                    - official_name (str): Official account name
                    - type (str): Account type
                    - subtype (str): Account subtype
                    - current_balance (float): Current balance
                    - available_balance (float): Available balance
                    - mask (str): Last 4 digits of account number
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/plaid/accounts', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['accounts'][0])
            {
                'account_id': '1234567890',
                'name': 'Checking Account',
                'official_name': 'Chase Checking',
                'type': 'depository',
                'subtype': 'checking',
                'current_balance': 1000.00,
                'available_balance': 950.00,
                'mask': '1234'
            }
        """
        try:
            user_id = get_jwt_identity()
            accounts = PlaidFacade.sync_accounts_for_user(user_id)
            
            # Convert accounts to dictionary format
            accounts_data = [{
                'account_id': acc.account_id,
                'name': acc.name,
                'official_name': acc.official_name,
                'type': acc.type,
                'subtype': acc.subtype,
                'current_balance': acc.current_balance,
                'available_balance': acc.available_balance,
                'mask': acc.mask
            } for acc in accounts]
            
            return {'accounts': accounts_data}, 200
            
        except APIConnectionError as e:
            return {"message": str(e)}, 500
        except ValueError as e:
            return {"message": str(e)}, 400
