from functools import wraps

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return ({'error': 'Validation Error', 'message': str(e)}), 400
        except Exception as e:
            return ({'error': 'Internal Server Error', 'message': str(e)}), 500
    return decorated_function
