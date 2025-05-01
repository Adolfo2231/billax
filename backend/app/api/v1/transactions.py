"""
Transaction Management API endpoints for financial operations.

This module provides REST API endpoints for managing financial transactions,
including listing, filtering, and synchronizing transactions with Plaid.
It handles operations such as transaction retrieval, account-specific lookups,
date range filtering, and pending transaction management.

Key Features:
- Transaction listing and filtering
- Account-specific transaction retrieval
- Date range filtering
- Pending transaction management
- Plaid transaction synchronization
- Secure access control with JWT tokens

Example:
    >>> # List all transactions for a user
    >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
    >>> response = client.get('/api/v1/transactions/', headers=headers)
    >>> print(response.status_code)
    200
    >>> print(response.json[0])
    {
        'id': 1,
        'transaction_id': 'txn_1234567890',
        'account_id': 'acc_1234567890',
        'amount': 50.00,
        'date': '2024-01-01',
        'name': 'Grocery Store',
        'merchant_name': 'Whole Foods',
        'category': ['Food', 'Groceries'],
        'pending': False,
        'created_at': '2024-01-01T12:00:00Z',
        'updated_at': '2024-01-01T12:00:00Z'
    }
"""

from typing import Dict, Any, List, Tuple, Optional
from flask_restx import Namespace, Resource, fields
from app.facades.plaid_facade import PlaidFacade
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.bank_account_repository import BankAccountRepository
from app.decorators import token_required
from datetime import datetime, date

# Create the transactions namespace
transactions_ns = Namespace('transactions', description='Transaction operations')

# Models for documentation
transaction_model = transactions_ns.model('Transaction', {
    'id': fields.Integer(description='Internal transaction ID'),
    'transaction_id': fields.String(description='Plaid transaction ID'),
    'account_id': fields.String(description='Plaid account ID'),
    'amount': fields.Float(description='Transaction amount'),
    'date': fields.String(description='Transaction date'),
    'name': fields.String(description='Transaction name'),
    'merchant_name': fields.String(description='Merchant name'),
    'category': fields.List(fields.String, description='Transaction categories'),
    'pending': fields.Boolean(description='Whether the transaction is pending'),
    'created_at': fields.String(description='When the transaction was created'),
    'updated_at': fields.String(description='When the transaction was last updated')
})


@transactions_ns.route('/')
class TransactionList(Resource):
    """
    Resource for listing all transactions.

    This endpoint provides access to all transactions associated with the
    authenticated user's bank accounts.
    """

    @transactions_ns.doc('list_transactions')
    @transactions_ns.marshal_list_with(transaction_model)
    @token_required
    def get(self, current_user) -> List[Dict[str, Any]]:
        """
        List all transactions for the current user's accounts.

        This endpoint retrieves all transactions associated with the
        authenticated user's bank accounts.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            List[Dict[str, Any]]: List of transaction objects

        Raises:
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/transactions/', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'id': 1,
                'transaction_id': 'txn_1234567890',
                'account_id': 'acc_1234567890',
                'amount': 50.00,
                'date': '2024-01-01',
                'name': 'Grocery Store',
                'merchant_name': 'Whole Foods',
                'category': ['Food', 'Groceries'],
                'pending': False,
                'created_at': '2024-01-01T12:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        """
        # Get all account IDs for the user
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        account_ids = [acc.account_id for acc in accounts]
        
        # Get all transactions for these accounts
        transactions = []
        for account_id in account_ids:
            transactions.extend(TransactionRepository().get_by_account_id(account_id))
            
        return transactions


@transactions_ns.route('/<string:transaction_id>')
class TransactionDetail(Resource):
    """
    Resource for transaction details.

    This endpoint provides detailed information about a specific transaction,
    including verification that it belongs to the authenticated user.
    """

    @transactions_ns.doc('get_transaction')
    @transactions_ns.marshal_with(transaction_model)
    @token_required
    def get(self, current_user, transaction_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get details of a specific transaction.

        This endpoint retrieves detailed information about a specific transaction
        and verifies that it belongs to one of the authenticated user's accounts.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            transaction_id (str): The Plaid transaction ID

        Returns:
            Tuple[Dict[str, Any], int]: Response containing:
                - transaction (dict): Transaction details
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 404: If transaction is not found or doesn't belong to user

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/transactions/txn_1234567890', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json)
            {
                'id': 1,
                'transaction_id': 'txn_1234567890',
                'account_id': 'acc_1234567890',
                'amount': 50.00,
                'date': '2024-01-01',
                'name': 'Grocery Store',
                'merchant_name': 'Whole Foods',
                'category': ['Food', 'Groceries'],
                'pending': False,
                'created_at': '2024-01-01T12:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        """
        transaction = TransactionRepository().get_by_transaction_id(transaction_id)
        if not transaction:
            return {'message': 'Transaction not found'}, 404
            
        # Verify the transaction belongs to one of the user's accounts
        account = BankAccountRepository().get_by_account_id(transaction.account_id)
        if not account or account.user_id != current_user.id:
            return {'message': 'Transaction not found'}, 404
            
        return transaction


@transactions_ns.route('/account/<string:account_id>')
class AccountTransactions(Resource):
    """
    Resource for account-specific transactions.

    This endpoint provides access to all transactions associated with a
    specific bank account, with verification that the account belongs to
    the authenticated user.
    """

    @transactions_ns.doc('list_account_transactions')
    @transactions_ns.marshal_list_with(transaction_model)
    @token_required
    def get(self, current_user, account_id: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        List all transactions for a specific account.

        This endpoint retrieves all transactions associated with a specific
        bank account and verifies that the account belongs to the
        authenticated user.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            account_id (str): The Plaid account ID

        Returns:
            Tuple[List[Dict[str, Any]], int]: Response containing:
                - transactions (list): List of transaction objects
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 404: If account is not found or doesn't belong to user

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/transactions/account/acc_1234567890', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'id': 1,
                'transaction_id': 'txn_1234567890',
                'account_id': 'acc_1234567890',
                'amount': 50.00,
                'date': '2024-01-01',
                'name': 'Grocery Store',
                'merchant_name': 'Whole Foods',
                'category': ['Food', 'Groceries'],
                'pending': False,
                'created_at': '2024-01-01T12:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        """
        # Verify the account belongs to the user
        account = BankAccountRepository().get_by_account_id(account_id)
        if not account or account.user_id != current_user.id:
            return {'message': 'Account not found'}, 404
            
        return TransactionRepository().get_by_account_id(account_id)


@transactions_ns.route('/date-range')
class DateRangeTransactions(Resource):
    """
    Resource for date range filtered transactions.

    This endpoint provides access to transactions within a specific date range,
    filtered across all of the authenticated user's bank accounts.
    """

    @transactions_ns.doc('list_date_range_transactions')
    @transactions_ns.expect(transactions_ns.model('DateRange', {
        'start_date': fields.String(required=True, description='Start date (YYYY-MM-DD)'),
        'end_date': fields.String(required=True, description='End date (YYYY-MM-DD)')
    }))
    @transactions_ns.marshal_list_with(transaction_model)
    @token_required
    def get(self, current_user) -> Tuple[List[Dict[str, Any]], int]:
        """
        List transactions within a date range.

        This endpoint retrieves all transactions within a specified date range
        across all of the authenticated user's bank accounts.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            Request body (JSON):
                - start_date (str): Start date in YYYY-MM-DD format
                - end_date (str): End date in YYYY-MM-DD format

        Returns:
            Tuple[List[Dict[str, Any]], int]: Response containing:
                - transactions (list): List of transaction objects
                - status_code (int): 200 for success

        Raises:
            HTTP 400: If date format is invalid or dates are missing
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> data = {
            ...     'start_date': '2024-01-01',
            ...     'end_date': '2024-01-31'
            ... }
            >>> response = client.get('/api/v1/transactions/date-range', json=data, headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'id': 1,
                'transaction_id': 'txn_1234567890',
                'account_id': 'acc_1234567890',
                'amount': 50.00,
                'date': '2024-01-01',
                'name': 'Grocery Store',
                'merchant_name': 'Whole Foods',
                'category': ['Food', 'Groceries'],
                'pending': False,
                'created_at': '2024-01-01T12:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        """
        start_date = transactions_ns.payload.get('start_date')
        end_date = transactions_ns.payload.get('end_date')
        
        if not start_date or not end_date:
            return {'message': 'Start date and end date are required'}, 400
            
        try:
            # Convert string dates to datetime.date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
            
        # Get all account IDs for the user
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        account_ids = [acc.account_id for acc in accounts]
        
        # Get transactions for these accounts within the date range
        transactions = []
        for account_id in account_ids:
            account_transactions = TransactionRepository().get_by_account_id(account_id)
            for tx in account_transactions:
                tx_date = tx.date if isinstance(tx.date, date) else datetime.strptime(tx.date, '%Y-%m-%d').date()
                if start_date <= tx_date <= end_date:
                    transactions.append(tx)
            
        return transactions


@transactions_ns.route('/pending')
class PendingTransactions(Resource):
    """
    Resource for pending transactions.

    This endpoint provides access to all pending transactions across
    the authenticated user's bank accounts.
    """

    @transactions_ns.doc('list_pending_transactions')
    @transactions_ns.marshal_list_with(transaction_model)
    @token_required
    def get(self, current_user) -> List[Dict[str, Any]]:
        """
        List all pending transactions.

        This endpoint retrieves all pending transactions across all of
        the authenticated user's bank accounts.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            List[Dict[str, Any]]: List of pending transaction objects

        Raises:
            HTTP 401: If no valid JWT token is provided

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/transactions/pending', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json[0])
            {
                'id': 1,
                'transaction_id': 'txn_1234567890',
                'account_id': 'acc_1234567890',
                'amount': 50.00,
                'date': '2024-01-01',
                'name': 'Grocery Store',
                'merchant_name': 'Whole Foods',
                'category': ['Food', 'Groceries'],
                'pending': True,
                'created_at': '2024-01-01T12:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        """
        # Get all account IDs for the user
        accounts = BankAccountRepository().get_by_user_id(current_user.id)
        account_ids = [acc.account_id for acc in accounts]
        
        # Get pending transactions for these accounts
        transactions = []
        for account_id in account_ids:
            account_transactions = TransactionRepository().get_by_account_id(account_id)
            transactions.extend([tx for tx in account_transactions if tx.pending])
            
        return transactions


@transactions_ns.route('/sync')
class SyncTransactions(Resource):
    """
    Resource for synchronizing transactions with Plaid.

    This endpoint triggers a synchronization of transactions with Plaid
    for a specified date range, updating the local database with the
    latest transaction data.
    """

    @transactions_ns.doc('sync_transactions')
    @transactions_ns.expect(transactions_ns.model('SyncRequest', {
        'start_date': fields.String(required=True, description='Start date (YYYY-MM-DD)'),
        'end_date': fields.String(required=True, description='End date (YYYY-MM-DD)')
    }))
    @token_required
    def post(self, current_user) -> Tuple[Dict[str, Any], int]:
        """
        Sync transactions with Plaid.

        This endpoint synchronizes transactions with Plaid for a specified
        date range, updating the local database with the latest transaction
        data from the user's linked bank accounts.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>
            Request body (JSON):
                - start_date (str): Start date in YYYY-MM-DD format
                - end_date (str): End date in YYYY-MM-DD format

        Returns:
            Tuple[Dict[str, Any], int]: Response containing:
                - message (str): Success message with number of synced transactions
                - transactions (list): List of synced transaction objects
                - status_code (int): 200 for success

        Raises:
            HTTP 400: If date format is invalid or dates are missing
            HTTP 401: If no valid JWT token is provided
            HTTP 500: For server errors

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> data = {
            ...     'start_date': '2024-01-01',
            ...     'end_date': '2024-01-31'
            ... }
            >>> response = client.post('/api/v1/transactions/sync', json=data, headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json['message'])
            Successfully synced 50 transactions
        """
        start_date = transactions_ns.payload.get('start_date')
        end_date = transactions_ns.payload.get('end_date')
        
        if not start_date or not end_date:
            return {'message': 'Start date and end date are required'}, 400
            
        try:
            transactions = PlaidFacade.sync_transactions(
                current_user.id,
                start_date,
                end_date
            )
            return {
                'message': f'Successfully synced {len(transactions)} transactions',
                'transactions': [tx.to_dict() for tx in transactions]
            }
        except Exception as e:
            return {'message': str(e)}, 500
