"""
models/account.py

This module defines the Account model for storing user's bank account information
retrieved from Plaid.
"""

from datetime import datetime
from app.extensions import db


class Account(db.Model):
    """
    Represents a bank account linked to a user through Plaid.

    Attributes:
        id (int): Unique integer primary key.
        user_id (int): Foreign key to the user who owns this account.
        plaid_account_id (str): Plaid's unique account identifier.
        name (str): Account name (e.g., "Chase Checking").
        type (str): Account type (e.g., "depository", "credit", "loan").
        subtype (str): Account subtype (e.g., "checking", "savings", "credit card").
        mask (str): Last 4 digits of the account number.
        current_balance (float): Current balance of the account.
        available_balance (float): Available balance of the account.
        limit (float): Credit limit (for credit accounts).
        currency_code (str): Currency code (e.g., "USD").
        is_active (bool): Whether the account is active.
        created_at (datetime): When the account was first synced.
        updated_at (datetime): When the account was last updated.
    """

    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plaid_account_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    subtype = db.Column(db.String(50), nullable=False)
    mask = db.Column(db.String(10), nullable=False)
    current_balance = db.Column(db.Numeric(15, 2), nullable=True)
    available_balance = db.Column(db.Numeric(15, 2), nullable=True)
    limit = db.Column(db.Numeric(15, 2), nullable=True)
    currency_code = db.Column(db.String(3), default='USD', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('accounts', lazy='dynamic'))

    def __repr__(self):
        """Returns a string representation of the account."""
        return f'<Account {self.name} ({self.mask})>'

    def to_dict(self):
        """Convert account to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plaid_account_id': self.plaid_account_id,
            'name': self.name,
            'type': self.type,
            'subtype': self.subtype,
            'mask': self.mask,
            'balances': {
                'current': float(self.current_balance) if self.current_balance is not None else 0.0,
                'available': float(self.available_balance) if self.available_balance is not None else 0.0,
                'limit': float(self.limit) if self.limit is not None else None
            },
            'currency_code': self.currency_code,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }