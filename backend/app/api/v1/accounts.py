"""
Bank Account Management API endpoints for financial operations.

This module provides REST API endpoints for managing bank accounts,
including listing accounts, retrieving account details, filtering by type,
and generating financial summaries. It handles operations such as account
retrieval, type-based filtering, and financial calculations.

Key Features:
- Account listing and filtering
- Account type management
- Financial summary generation
- Balance tracking
- Secure access control with JWT tokens

Example:
    >>> # List all bank accounts for a user
    >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
    >>> response = client.get('/api/v1/accounts/', headers=headers)
    >>> print(response.status_code)
    200
    >>> print(response.json[0])
    {
        'account_id': 'acc_1234567890',
        'name': 'Checking Account',
        'official_name': 'Chase Checking Account',
        'type': 'depository',
        'subtype': 'checking',
        'current_balance': 1500.00,
        'available_balance': 1500.00,
        'mask': '1234'
    }
"""

from typing import Dict, Any, List, Tuple, Optional
from flask_restx import Namespace, Resource, fields
from app.facades.plaid_facade import PlaidFacade
from app.repositories.bank_account_repository import BankAccountRepository
from app.decorators import token_required

# Create the accounts namespace
accounts_ns = Namespace('accounts', description='Bank account operations')

# Models for documentation
account_model = accounts_ns.model('BankAccount', {
    'account_id': fields.String(description='Plaid account ID'),
    'name': fields.String(description='Account name'),
    'official_name': fields.String(description='Official account name'),
    'type': fields.String(description='Account type (depository, credit, investment, loan)'),
    'subtype': fields.String(description='Account subtype'),
    'current_balance': fields.Float(description='Current balance'),
    'available_balance': fields.Float(description='Available balance'),
    'mask': fields.String(description='Last 4 digits of account number')
})


@accounts_ns.route('/')
class AccountList(Resource):
    """
    Resource for listing all bank accounts.

    This endpoint provides access to all bank accounts associated with the
    authenticated user, including checking, savings, credit, and investment
    accounts.
    """

    @accounts_ns.doc('list_accounts')
    @accounts_ns.marshal_list_with(account_model)
    @token_required
    def get(self, current_user) -> List[Dict[str, Any]]:
        """
        List all bank accounts for the current user.

        This endpoint retrieves all bank accounts associated with the
        authenticated user, including their balances and account details.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            List[Dict[str, Any]]: List of bank account objects

        Raises:
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/accounts/', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'account_id': 'acc_1234567890',
                'name': 'Checking Account',
                'official_name': 'Chase Checking Account',
                'type': 'depository',
                'subtype': 'checking',
                'current_balance': 1500.00,
                'available_balance': 1500.00,
                'mask': '1234'
            }
        """
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        return accounts


@accounts_ns.route('/<string:account_id>')
class AccountDetail(Resource):
    """
    Resource for account details.

    This endpoint provides detailed information about a specific bank account,
    including verification that it belongs to the authenticated user.
    """

    @accounts_ns.doc('get_account')
    @accounts_ns.marshal_with(account_model)
    @token_required
    def get(self, current_user, account_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get details of a specific bank account.

        This endpoint retrieves detailed information about a specific bank
        account and verifies that it belongs to the authenticated user.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            account_id (str): The Plaid account ID

        Returns:
            Tuple[Dict[str, Any], int]: Response containing:
                - account (dict): Account details
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 404: If account is not found or doesn't belong to user

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/accounts/acc_1234567890', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json)
            {
                'account_id': 'acc_1234567890',
                'name': 'Checking Account',
                'official_name': 'Chase Checking Account',
                'type': 'depository',
                'subtype': 'checking',
                'current_balance': 1500.00,
                'available_balance': 1500.00,
                'mask': '1234'
            }
        """
        account = BankAccountRepository().get_by_account_id(account_id)
        if not account or account.user_id != current_user.id:
            return {'message': 'Account not found'}, 404
        return account


@accounts_ns.route('/types/<string:account_type>')
class AccountTypeList(Resource):
    """
    Resource for type-specific accounts.

    This endpoint provides access to bank accounts filtered by type,
    such as checking, savings, credit, or investment accounts.
    """

    @accounts_ns.doc('list_accounts_by_type')
    @accounts_ns.marshal_list_with(account_model)
    @token_required
    def get(self, current_user, account_type: str) -> List[Dict[str, Any]]:
        """
        List accounts filtered by type.

        This endpoint retrieves all bank accounts of a specific type
        associated with the authenticated user.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            account_type (str): The account type to filter by
                (depository, credit, investment, loan)

        Returns:
            List[Dict[str, Any]]: List of bank account objects

        Raises:
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/accounts/types/depository', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'account_id': 'acc_1234567890',
                'name': 'Checking Account',
                'official_name': 'Chase Checking Account',
                'type': 'depository',
                'subtype': 'checking',
                'current_balance': 1500.00,
                'available_balance': 1500.00,
                'mask': '1234'
            }
        """
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        filtered_accounts = [acc for acc in accounts if acc.type == account_type]
        return filtered_accounts


@accounts_ns.route('/summary')
class AccountSummary(Resource):
    """
    Resource for financial summary.

    This endpoint provides a comprehensive financial summary across all
    of the authenticated user's bank accounts, including total assets,
    liabilities, and net worth calculations.
    """

    @accounts_ns.doc('get_account_summary')
    @token_required
    def get(self, current_user) -> Dict[str, Any]:
        """
        Get financial summary for all accounts.

        This endpoint calculates and returns a comprehensive financial
        summary across all of the authenticated user's bank accounts,
        including:
        - Total assets (depository and investment accounts)
        - Total liabilities (credit and loan accounts)
        - Net worth (assets - liabilities)
        - Account type distribution

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Dict[str, Any]: Financial summary containing:
                - total_assets (float): Sum of all asset accounts
                - total_liabilities (float): Sum of all liability accounts
                - net_worth (float): Total assets minus total liabilities
                - account_types (dict): Count of accounts by type

        Raises:
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/accounts/summary', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json)
            {
                'total_assets': 50000.00,
                'total_liabilities': 10000.00,
                'net_worth': 40000.00,
                'account_types': {
                    'depository': 2,
                    'credit': 1,
                    'investment': 1,
                    'loan': 0
                }
            }
        """
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        
        summary = {
            'total_assets': 0.0,
            'total_liabilities': 0.0,
            'net_worth': 0.0,
            'account_types': {
                'depository': 0,
                'credit': 0,
                'investment': 0,
                'loan': 0
            }
        }
        
        for account in accounts:
            # Count account types
            summary['account_types'][account.type] += 1
            
            # Calculate balances
            if account.type in ['depository', 'investment']:
                summary['total_assets'] += account.current_balance
            elif account.type in ['credit', 'loan']:
                summary['total_liabilities'] += account.current_balance
        
        summary['net_worth'] = summary['total_assets'] - summary['total_liabilities']
        
        return summary
