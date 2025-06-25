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
    
    def get_by_type_and_user(self, user_id: int, transaction_type: str) -> List[Transaction]:
        """Get transactions by type and user ID"""
        return Transaction.query.filter_by(
            user_id=user_id, 
            category_primary=transaction_type
        ).order_by(Transaction.date.desc()).all()
    
    def delete(self, transaction_id: int) -> None:
        """Delete a transaction by ID"""
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
    
    def delete_all_by_user_id(self, user_id: int) -> None:
        """Delete all transactions for a user"""
        Transaction.query.filter_by(user_id=user_id).delete()
        db.session.commit()