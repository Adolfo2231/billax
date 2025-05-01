"""
Transaction model for storing transaction data from Plaid.

This module defines the Transaction model for storing financial transaction data
retrieved from Plaid. It handles the storage and representation of transaction
details including amounts, dates, merchants, and categories.

The model supports:
- Transaction identification and tracking
- Amount and date storage
- Merchant information
- Transaction categorization
- Pending status tracking
- Timestamp management

Example:
    >>> transaction = Transaction(
    ...     transaction_id="txn_123",
    ...     account_id="acc_456",
    ...     amount=50.00,
    ...     date=datetime(2024, 3, 25),
    ...     name="Grocery Store",
    ...     merchant_name="Whole Foods",
    ...     category=["Food and Drink", "Groceries"],
    ...     pending=False
    ... )
    >>> transaction.amount
    50.00
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
from app.extensions import db


class Transaction(db.Model):
    """
    Transaction model for storing financial transaction data.

    This model represents a financial transaction from a bank account,
    storing details such as amount, date, merchant, and categorization.

    Attributes:
        id (int): Primary key for the transaction record.
        transaction_id (str): Unique identifier from Plaid for this transaction.
        account_id (str): Identifier of the associated bank account.
        amount (float): Transaction amount (positive for credits, negative for debits).
        date (datetime.date): Date when the transaction occurred.
        name (str): Name or description of the transaction.
        merchant_name (Optional[str]): Name of the merchant if available.
        category (Optional[List[str]]): Transaction categories from Plaid.
        pending (bool): Whether the transaction is pending or settled.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.

    Example:
        >>> transaction = Transaction(
        ...     transaction_id="txn_123",
        ...     account_id="acc_456",
        ...     amount=50.00,
        ...     date=datetime(2024, 3, 25),
        ...     name="Grocery Store",
        ...     merchant_name="Whole Foods",
        ...     category=["Food and Drink", "Groceries"],
        ...     pending=False
        ... )
        >>> transaction.amount
        50.00
    """

    __tablename__: str = 'transactions'
    
    id: int = db.Column(db.Integer, primary_key=True)
    transaction_id: str = db.Column(db.String(100), unique=True, nullable=False)
    account_id: str = db.Column(db.String(100), nullable=False)
    amount: float = db.Column(db.Float, nullable=False)
    date: datetime = db.Column(db.Date, nullable=False)
    name: str = db.Column(db.String(200), nullable=False)
    merchant_name: Optional[str] = db.Column(db.String(200))
    category: Optional[List[str]] = db.Column(db.JSON)
    pending: bool = db.Column(db.Boolean, default=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """
        Returns a human-readable representation of the transaction.

        Returns:
            str: A string containing the transaction ID.

        Example:
            >>> transaction = Transaction(transaction_id="txn_123")
            >>> repr(transaction)
            '<Transaction txn_123>'
        """
        return f'<Transaction {self.transaction_id}>'
        
    def to_dict(self) -> Dict[str, Union[int, str, float, bool, List[str], None]]:
        """
        Convert transaction to dictionary format.

        Returns:
            Dict[str, Union[int, str, float, bool, List[str], None]]: Dictionary containing
            all transaction fields with appropriate types.

        Example:
            >>> transaction = Transaction(
            ...     transaction_id="txn_123",
            ...     account_id="acc_456",
            ...     amount=50.00,
            ...     date=datetime(2024, 3, 25),
            ...     name="Grocery Store"
            ... )
            >>> transaction_dict = transaction.to_dict()
            >>> transaction_dict['amount']
            50.00
        """
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'name': self.name,
            'merchant_name': self.merchant_name,
            'category': self.category,
            'pending': self.pending,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
