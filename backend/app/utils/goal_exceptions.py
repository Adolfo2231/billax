class GoalError(Exception):
    """Base exception for goal-related errors"""
    


class GoalNotFoundError(GoalError):
    """Raised when a goal is not found"""
    pass


class GoalValidationError(GoalError):
    """Raised when goal data validation fails"""
    pass


class GoalPermissionError(GoalError):
    """Raised when user doesn't have permission to access a goal"""
    pass 