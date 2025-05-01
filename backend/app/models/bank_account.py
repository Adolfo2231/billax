"""
models/bank_account.py

This module defines the BankAccount model for the finance application using Flask-SQLAlchemy.
It represents a bank account linked to a user through Plaid integration.

The BankAccount model handles:
- Storage of bank account details
- Association with users
- Balance tracking
- Account type categorization

Example:
    >>> account = BankAccount(
    ...     user_id="user-uuid",
    ...     account_id="plaid-account-id",
    ...     name="Checking Account",
    ...     type="depository",
    ...     subtype="checking",
    ...     current_balance=1000.00
    ... )
    >>> account.current_balance
    1000.00
"""

from typing import Optional
from app.extensions import db


class BankAccount(db.Model):
    """
    Represents a bank account in the finance application.

    This model stores information about bank accounts linked through Plaid,
    including balances, account types, and user associations.

    Attributes:
        id (int): Primary key for the account record.
        user_id (str): Foreign key referencing the user who owns this account.
        account_id (str): Unique identifier from Plaid for this account.
        name (str): Display name of the account.
        official_name (Optional[str]): Official name of the account from the bank.
        type (str): Main account type (e.g., 'depository', 'credit', 'loan').
        subtype (str): Specific account subtype (e.g., 'checking', 'savings').
        current_balance (float): Current balance of the account.
        available_balance (Optional[float]): Available balance for spending.
        mask (Optional[str]): Last 4 digits of the account number.

    Example:
        >>> account = BankAccount(
        ...     user_id="user-uuid",
        ...     account_id="plaid-account-id",
        ...     name="Checking Account",
        ...     type="depository",
        ...     subtype="checking",
        ...     current_balance=1000.00
        ... )
        >>> account.current_balance
        1000.00
    """

    __tablename__: str = "bank_accounts"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: str = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    account_id: str = db.Column(db.String(100), unique=True, nullable=False)
    name: str = db.Column(db.String(120), nullable=False)
    official_name: Optional[str] = db.Column(db.String(200), nullable=True)
    type: str = db.Column(db.String(50), nullable=False)
    subtype: str = db.Column(db.String(50), nullable=False)
    current_balance: float = db.Column(db.Float, nullable=False)
    available_balance: Optional[float] = db.Column(db.Float, nullable=True)
    mask: Optional[str] = db.Column(db.String(10), nullable=True)

    def __repr__(self) -> str:
        """
        Returns a human-readable representation of the bank account.

        Returns:
            str: A string containing the account name, type, and current balance.

        Example:
            >>> account = BankAccount(
            ...     user_id="user-uuid",
            ...     account_id="plaid-account-id",
            ...     name="Checking Account",
            ...     type="depository",
            ...     subtype="checking",
            ...     current_balance=1000.00
            ... )
            >>> repr(account)
            "<BankAccount(name='Checking Account', type='depository', balance=1000.0)>"
        """
        return f"<BankAccount(name='{self.name}', type='{self.type}', balance={self.current_balance})>"
