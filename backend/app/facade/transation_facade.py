from app.services.plaid_config import sync_transactions
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.utils.plaid_exceptions import PlaidUserNotLinkedError, UserNotFoundError
from app.utils.transaction_exceptions import TransactionNotFoundError, TransactionTypeNotFoundError
from typing import Dict, Any
from datetime import datetime

class TransactionFacade:
    def __init__(self):
        self.user_repository = UserRepository()
        self.transaction_repository = TransactionRepository()

    def sync_transactions(self, user_id: str, start_date: str = None, end_date: str = None, count: int = None) -> Dict[str, Any]:
        """
        Retrieves transaction information from Plaid for a user and saves to database.

        This method retrieves transactions from Plaid for a given date range and
        saves them to the database, avoiding duplicates.

        Args:
            user_id (str): The user ID.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            count (int): Number of transactions to retrieve (optional, if not specified gets all).

        Returns:
            Dict[str, Any]: Dictionary containing summary of synced transactions.

        Raises:
            UserNotFoundError: If the user is not found.
            PlaidUserNotLinkedError: If the user is not connected to Plaid.
            PlaidDataSyncError: If there is an error retrieving transaction data.
        """
        # Validate user and Plaid connection
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if not user.plaid_access_token:
            raise PlaidUserNotLinkedError()
        
        # Get transactions from Plaid
        result = sync_transactions(user_id, start_date, end_date, count)
        
        # Save transactions to database
        saved_count = self._save_transactions_to_db(result.get('transactions', []), int(user_id))
        
        # Return clean summary
        return {
            "message": "Transactions synced successfully",
            "summary": {
                "total_plaid_transactions": len(result.get('transactions', [])),
                "new_transactions_saved": saved_count,
                "existing_transactions_skipped": len(result.get('transactions', [])) - saved_count,
                "date_range": {
                    "start_date": start_date or "90 days ago",
                    "end_date": end_date or "today"
                }
            },
            "accounts_count": len(result.get('accounts', [])),
            "has_more": result.get('has_more', False)
        }
    
    def _save_transactions_to_db(self, transactions: list, user_id: int) -> int:
        """Save transactions to database, avoiding duplicates"""
        saved_count = 0
        
        for tx in transactions:
            # Check if transaction already exists
            if self.transaction_repository.exists_by_plaid_id(tx['transaction_id']):
                continue
            
            # Prepare transaction data for database
            transaction_data = {
                'plaid_transaction_id': tx['transaction_id'],
                'account_id': tx['account_id'],
                'user_id': user_id,
                'name': tx['name'],
                'amount': tx['amount'],
                'date': datetime.strptime(tx['date'], '%Y-%m-%d').date(),
                'authorized_date': datetime.strptime(tx['authorized_date'], '%Y-%m-%d').date() if tx.get('authorized_date') else None,
                'merchant_name': tx.get('merchant_name'),
                'merchant_entity_id': tx.get('merchant_entity_id'),
                'logo_url': tx.get('logo_url'),
                'website': tx.get('website'),
                'category_primary': tx.get('personal_finance_category', {}).get('primary'),
                'category_detailed': tx.get('personal_finance_category', {}).get('detailed'),
                'category_confidence': tx.get('personal_finance_category', {}).get('confidence_level'),
                'payment_channel': tx.get('payment_channel'),
                'payment_method': tx.get('payment_meta', {}).get('payment_method'),
                'pending': tx.get('pending', False),
                'location_address': tx.get('location', {}).get('address'),
                'location_city': tx.get('location', {}).get('city'),
                'location_region': tx.get('location', {}).get('region'),
                'location_postal_code': tx.get('location', {}).get('postal_code'),
                'location_country': tx.get('location', {}).get('country'),
                'location_lat': tx.get('location', {}).get('lat'),
                'location_lon': tx.get('location', {}).get('lon'),
                'transaction_type': tx.get('transaction_type'),
                'transaction_code': tx.get('transaction_code'),
                'check_number': tx.get('check_number')
            }
            
            # Save transaction
            self.transaction_repository.create(transaction_data)
            saved_count += 1
        
        return saved_count
    
    def get_user_transactions(self, user_id: str, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get transactions from database for a user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        transactions = self.transaction_repository.get_by_user_id(int(user_id), limit, offset)
        
        return {
            "transactions": [tx.to_dict() for tx in transactions],
            "total_count": self.transaction_repository.count_by_user_id(int(user_id)),
            "returned_count": len(transactions)
        }
    
    def get_transaction_by_id(self, user_id: str, transaction_id: int) -> Dict[str, Any]:
        """Get transaction by ID"""
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise TransactionNotFoundError()
        
        # Validate that the transaction belongs to the user
        if transaction.user_id != int(user_id):
            raise TransactionNotFoundError()
            
        return transaction.to_dict()
    
    def get_transactions_by_type(self, user_id: str, transaction_type: str) -> Dict[str, Any]:
        """Get transactions by type for a specific user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        transactions = self.transaction_repository.get_by_type_and_user(int(user_id), transaction_type)
        
        if not transactions:
            raise TransactionTypeNotFoundError()
        
        return {
            "transactions": [tx.to_dict() for tx in transactions],
            "total_count": len(transactions),
            "transaction_type": transaction_type
        }
    
    def delete_transaction(self, user_id: str, transaction_id: int) -> Dict[str, Any]:
        """Delete a transaction by ID"""
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise TransactionNotFoundError()
        
        # Validate that the transaction belongs to the user
        if transaction.user_id != int(user_id):
            raise TransactionNotFoundError()
        
        self.transaction_repository.delete(transaction_id)
        return {"message": "Transaction deleted successfully"}
    
    def delete_all_transactions(self, user_id: str) -> Dict[str, Any]:
        """Delete all transactions for a user"""
        self.transaction_repository.delete_all_by_user_id(int(user_id))
        return {"message": "All transactions deleted successfully"}