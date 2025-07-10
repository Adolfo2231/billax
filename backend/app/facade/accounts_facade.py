from typing import List, Dict, Any
from app.services.plaid_config import sync_accounts
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.models.account import Account
from app.utils.plaid_exceptions import PlaidUserNotFoundError, PlaidUserNotLinkedError
from app.utils.accounts_exceptions import AccountNotFoundError

class AccountsFacade:
    def __init__(self):
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()

    def sync_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's bank accounts from Plaid and sync to database."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        if not user.plaid_access_token:
            raise PlaidUserNotLinkedError("User is not linked to Plaid")
        
        # Get accounts from Plaid
        plaid_accounts = sync_accounts(user.plaid_access_token)
        
        # Convert Plaid data to Account models and save to database
        accounts_to_save = []
        for plaid_account in plaid_accounts:
            balances = plaid_account.get('balances', {})
            
            account = Account(
                user_id=user_id,
                plaid_account_id=plaid_account['account_id'],
                name=plaid_account['name'],
                type=plaid_account['type'],
                subtype=plaid_account['subtype'],
                mask=plaid_account['mask'],
                current_balance=balances.get('current'),
                available_balance=balances.get('available'),
                limit=balances.get('limit'),
                currency_code=balances.get('iso_currency_code', 'USD')
            )
            accounts_to_save.append(account)
        
        # Save all accounts to database
        self.account_repository.bulk_save_or_update(accounts_to_save)
        
        # Return accounts from database
        saved_accounts = self.account_repository.get_by_user_id(user_id)
        return [account.to_dict() for account in saved_accounts]
    
    def get_account_by_id(self, user_id: int, account_id: int) -> Dict[str, Any]:
        """Get an account by its ID, ensuring it belongs to the user."""
        account = self.account_repository.get_by_id_and_user_id(account_id, user_id)
        if not account:
            raise AccountNotFoundError()
        return account.to_dict()
    
    def get_accounts_by_type(self, user_id: int, account_type: str) -> List[Dict[str, Any]]:
        """Get accounts by type."""
        accounts = self.account_repository.get_by_user_id_and_type(user_id, account_type)
        if not accounts:
            raise AccountNotFoundError()
        return [account.to_dict() for account in accounts]
    
    def delete_accounts(self, user_id: int):
        """Delete all accounts for a user."""
        self.account_repository.delete_by_user_id(user_id)
        return {"message": "Accounts deleted successfully"}

    def get_accounts_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of all accounts for a user."""
        accounts = self.account_repository.get_by_user_id(user_id)
        if not accounts:
            raise AccountNotFoundError()
        
        # Initialize summary structure
        summary = {
            "total_accounts": len(accounts),
            "total_balance": 0.0,
            "accounts_by_type": {},
            "accounts_by_status": {
                "active": {"count": 0, "total_balance": 0.0},
                "pending": {"count": 0, "total_balance": 0.0}
            },
            "balance_trend": {
                "available": 0.0,
                "current": 0.0,
                "limit": 0.0
            }
        }
        
        for account in accounts:
            # Convert Decimal to float to avoid type conflicts
            current_balance = float(account.current_balance or 0.0)
            available_balance = float(account.available_balance or 0.0)
            limit = float(account.limit or 0.0)
            
            # Add to total balance
            summary["total_balance"] += current_balance
            
            # Group by account type
            account_type = account.type
            if account_type not in summary["accounts_by_type"]:
                summary["accounts_by_type"][account_type] = {
                    "count": 0,
                    "total_balance": 0.0
                }
            summary["accounts_by_type"][account_type]["count"] += 1
            summary["accounts_by_type"][account_type]["total_balance"] += current_balance
            
            # Group by status (active vs pending)
            if current_balance >= 0:
                summary["accounts_by_status"]["active"]["count"] += 1
                summary["accounts_by_status"]["active"]["total_balance"] += current_balance
            else:
                summary["accounts_by_status"]["pending"]["count"] += 1
                summary["accounts_by_status"]["pending"]["total_balance"] += current_balance
            
            # Balance trend
            summary["balance_trend"]["available"] += available_balance
            summary["balance_trend"]["current"] += current_balance
            summary["balance_trend"]["limit"] += limit
        
        return summary
    
    def get_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all accounts for a user."""
        accounts = self.account_repository.get_by_user_id(user_id)
        if not accounts:
            raise AccountNotFoundError()
        return [account.to_dict() for account in accounts]
    
    def delete_account(self, user_id: int, account_id: int):
        """Delete an account for a user."""
        self.account_repository.delete_by_id_and_user_id(account_id, user_id)
        return {"message": "Account deleted successfully"}