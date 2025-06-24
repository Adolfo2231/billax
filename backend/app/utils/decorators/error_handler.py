from functools import wraps
from app.utils.plaid_exceptions import PlaidTokenError, PlaidDataSyncError, PlaidUserNotLinkedError, PlaidUserAlreadyLinkedError, PlaidUserNotFoundError
from app.utils.accounts_exceptions import AccountNotFoundError
from app.utils.transaction_exceptions import TransactionNotFoundError, TransactionTypeNotFoundError

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AccountNotFoundError, TransactionNotFoundError, TransactionTypeNotFoundError) as e:
            return ({'message': str(e)}), 404
        except (PlaidTokenError, PlaidUserNotLinkedError, PlaidUserAlreadyLinkedError, PlaidUserNotFoundError) as e:
            return ({'message': str(e)}), 400
        except PlaidDataSyncError as e:
            return ({'message': str(e)}), 500
        except ValueError as e:
            error_message = str(e).lower()
            
            # Check if it's an authentication/authorization error
            auth_errors = [
                'invalid credentials',
                'invalid token',
                'invalid or expired reset token',
                'invalid reset token',
                'user not found'
            ]
            
            if any(auth_error in error_message for auth_error in auth_errors):
                return ({'message': str(e)}), 401
            else:
                return ({'message': str(e)}), 400
        except Exception as e:
            return ({'message': str(e)}), 500
    return decorated_function
