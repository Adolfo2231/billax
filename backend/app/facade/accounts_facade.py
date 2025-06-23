from typing import List, Dict, Any
from app.services.plaid_config import get_accounts
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.models.account import Account
from app.utils.plaid_exceptions import PlaidUserNotFoundError, PlaidUserNotLinkedError
from app.utils.accounts_exceptions import AccountNotFoundError

class AccountsFacade:
    def __init__(self):
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()

    def get_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's bank accounts from Plaid and sync to database."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        if not user.plaid_access_token:
            raise PlaidUserNotLinkedError("User is not linked to Plaid")
        
        # Get accounts from Plaid
        plaid_accounts = get_accounts(user.plaid_access_token)
        
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

