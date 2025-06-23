"""
repositories/account_repository.py

This module provides data access methods for Account entities.
"""

from typing import List, Optional
from app.models.account import Account
from app.extensions import db


class AccountRepository:
    """
    Repository for Account entity operations.
    """

    def get_by_user_id(self, user_id: int) -> List[Account]:
        """
        Get all active accounts for a specific user.
        
        Args:
            user_id (int): The user ID.
            
        Returns:
            List[Account]: List of active accounts for the user.
        """
        return Account.query.filter_by(user_id=user_id, is_active=True).all()

    def save(self, account: Account) -> Account:
        """
        Save an account to the database.
        
        Args:
            account (Account): The account to save.
            
        Returns:
            Account: The saved account.
        """
        db.session.add(account)
        db.session.commit()
        return account

    def bulk_save_or_update(self, accounts: List[Account]) -> List[Account]:
        """
        Save or update multiple accounts in bulk.
        
        Args:
            accounts (List[Account]): List of accounts to save or update.
            
        Returns:
            List[Account]: List of saved/updated accounts.
        """
        for account in accounts:
            # Check if account already exists by plaid_account_id
            existing_account = Account.query.filter_by(
                plaid_account_id=account.plaid_account_id
            ).first()
            
            if existing_account:
                # Update existing account
                existing_account.name = account.name
                existing_account.type = account.type
                existing_account.subtype = account.subtype
                existing_account.mask = account.mask
                existing_account.current_balance = account.current_balance
                existing_account.available_balance = account.available_balance
                existing_account.limit = account.limit
                existing_account.currency_code = account.currency_code
                existing_account.is_active = True  # Always set to True for existing accounts
            else:
                # Add new account
                db.session.add(account)
        
        db.session.commit()
        return accounts
    
    def get_by_id_and_user_id(self, account_id: int, user_id: int) -> Optional[Account]:
        """
        Get an account by its ID and user ID for security.
        
        Args:
            account_id (int): The account ID.
            user_id (int): The user ID.
            
        Returns:
            Optional[Account]: The account if found and belongs to user, None otherwise.
        """
        return Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first()
    
    def get_by_user_id_and_type(self, user_id: int, account_type: str) -> List[Account]:
        """
        Get accounts by user ID and account type.
        
        Args:
            user_id (int): The user ID.
            account_type (str): The account type (e.g., 'depository', 'credit', 'loan', 'investment').
            
        Returns:
            List[Account]: List of accounts matching the criteria.
        """
        return Account.query.filter_by(user_id=user_id, type=account_type, is_active=True).all()