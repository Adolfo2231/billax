from functools import wraps
from app.utils.plaid_exceptions import PlaidTokenError, PlaidDataSyncError, PlaidUserNotLinkedError, PlaidUserAlreadyLinkedError, PlaidUserNotFoundError

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PlaidTokenError as e:
            return ({'error': 'Plaid Token Error', 'message': str(e)}), 400
        except PlaidDataSyncError as e:
            return ({'error': 'Plaid Data Sync Error', 'message': str(e)}), 500
        except PlaidUserNotLinkedError as e:
            return ({'error': 'Plaid User Not Linked', 'message': str(e)}), 400
        except PlaidUserAlreadyLinkedError as e:
            return ({'error': 'Plaid User Already Linked', 'message': str(e)}), 400
        except PlaidUserNotFoundError as e:
            return ({'error': 'Plaid User Not Found', 'message': str(e)}), 400
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
                return ({'error': 'Authentication Error', 'message': str(e)}), 401
            else:
                return ({'error': 'Validation Error', 'message': str(e)}), 400
        except Exception as e:
            return ({'error': 'Internal Server Error', 'message': str(e)}), 500
    return decorated_function
