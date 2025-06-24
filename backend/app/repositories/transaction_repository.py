from app.models.transaction import Transaction
from app.extensions import db
from typing import List, Dict, Any, Optional

class TransactionRepository:
    
    def create(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(**transaction_data)
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def get_by_user_id(self, user_id: int, limit: int = None, offset: int = 0) -> List[Transaction]:
        """Get transactions by user ID"""
        query = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def count_by_user_id(self, user_id: int) -> int:
        """Count transactions for a user"""
        return Transaction.query.filter_by(user_id=user_id).count()
    
    def exists_by_plaid_id(self, plaid_transaction_id: str) -> bool:
        """Check if transaction exists by Plaid ID"""
        return Transaction.query.filter_by(plaid_transaction_id=plaid_transaction_id).first() is not None 
    
    def get_by_id(self, transaction_id: int) -> Transaction:
        """Get transaction by ID"""
        return Transaction.query.get(transaction_id)