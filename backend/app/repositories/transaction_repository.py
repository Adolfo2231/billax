from app.models.transaction import Transaction
from app.extensions import db
from typing import List, Dict, Any


class TransactionRepository:
    
    def create(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(**transaction_data)
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def get_by_user_id(self, user_id: int, limit: int = None, offset: int = 0, start_date: str = None, end_date: str = None) -> List[Transaction]:
        """Get transactions by user ID, optionally filtered by date range"""
        query = Transaction.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        query = query.order_by(Transaction.date.desc())
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
    
    def get_by_type(self, transaction_type: str) -> List[Transaction]:
        """Get transactions by type"""
        return Transaction.query.filter_by(type=transaction_type).all()
    
    def get_by_type_and_user(self, user_id: int, transaction_type: str) -> List[Transaction]:
        """Get transactions by type and user ID"""
        return Transaction.query.filter_by(
            user_id=user_id, 
            category_primary=transaction_type
        ).order_by(Transaction.date.desc()).all()
    
    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        """Get transactions by account ID (plaid_account_id)"""
        return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.date.desc()).all()
    
    def get_summary_by_user_id(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive transaction summary for a user"""
        # Get all transactions for the user
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        if not transactions:
            return {
                "total_transactions": 0,
                "total_spent": 0.0,
                "total_income": 0.0,
                "net_flow": 0.0,
                "categories": {},
                "monthly_trends": {},
                "top_merchants": [],
                "payment_analysis": {},
                "transaction_stats": {}
            }
        
        # Calculate basic totals
        total_spent = sum(float(tx.amount) for tx in transactions if tx.amount > 0)
        total_income = abs(sum(float(tx.amount) for tx in transactions if tx.amount < 0))
        net_flow = total_income - total_spent
        
        # Group by categories
        categories = {}
        for tx in transactions:
            category = tx.category_primary or "UNCATEGORIZED"
            if category not in categories:
                categories[category] = {"count": 0, "total": 0.0}
            categories[category]["count"] += 1
            categories[category]["total"] += float(tx.amount)
        
        # Calculate percentages for categories
        total_transactions = len(transactions)
        for category in categories:
            categories[category]["percentage"] = round(
                (categories[category]["count"] / total_transactions) * 100, 1
            )
        
        # Monthly trends
        monthly_trends = {}
        for tx in transactions:
            month_key = tx.date.strftime("%Y-%m")
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {"count": 0, "total": 0.0}
            monthly_trends[month_key]["count"] += 1
            monthly_trends[month_key]["total"] += float(tx.amount)
        
        # Top merchants
        merchant_stats = {}
        for tx in transactions:
            merchant = tx.merchant_name or tx.name
            if merchant not in merchant_stats:
                merchant_stats[merchant] = {"count": 0, "total": 0.0}
            merchant_stats[merchant]["count"] += 1
            merchant_stats[merchant]["total"] += float(tx.amount)
        
        # Sort merchants by total spent and get top 5
        top_merchants = sorted(
            [{"name": k, "count": v["count"], "total": v["total"]} 
             for k, v in merchant_stats.items()],
            key=lambda x: x["total"],
            reverse=True
        )[:5]
        
        # Payment channel analysis
        payment_analysis = {}
        for tx in transactions:
            channel = tx.payment_channel or "unknown"
            if channel not in payment_analysis:
                payment_analysis[channel] = {"count": 0}
            payment_analysis[channel]["count"] += 1
        
        # Calculate percentages for payment channels
        for channel in payment_analysis:
            payment_analysis[channel]["percentage"] = round(
                (payment_analysis[channel]["count"] / total_transactions) * 100, 1
            )
        
        # Transaction statistics
        amounts = [float(tx.amount) for tx in transactions]
        transaction_stats = {
            "highest_transaction": max(amounts),
            "lowest_transaction": min(amounts),
            "average_transaction": round(sum(amounts) / len(amounts), 2),
            "pending_transactions": len([tx for tx in transactions if tx.pending]),
            "completed_transactions": len([tx for tx in transactions if not tx.pending])
        }
        
        return {
            "total_transactions": total_transactions,
            "total_spent": round(total_spent, 2),
            "total_income": round(total_income, 2),
            "net_flow": round(net_flow, 2),
            "categories": categories,
            "monthly_trends": monthly_trends,
            "top_merchants": top_merchants,
            "payment_analysis": payment_analysis,
            "transaction_stats": transaction_stats
        }
    
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