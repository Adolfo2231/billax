from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.repositories.goal_repository import GoalRepository
from app.repositories.user_repository import UserRepository
from app.utils.goal_exceptions import GoalNotFoundError, GoalValidationError, GoalPermissionError
from app.repositories.account_repository import AccountRepository
from app.models.goal import Goal


class GoalFacade:
    """Facade for goal business logic"""

    # Constants
    VALID_CATEGORIES = ['savings', 'investment', 'debt', 'emergency', 'vacation', 'education', 'bills', 'other']
    VALID_STATUSES = ['active', 'completed', 'cancelled']
    VALID_FIELDS = ['title', 'description', 'target_amount', 'deadline', 'category', 'status', 'linked_account_id', 'linked_amount']

    def __init__(self):
        self.goal_repository: GoalRepository = GoalRepository()
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()

    def _validate_linked_amount_total(self, user_id, linked_account_id, linked_amount, exclude_goal_id=None):
        """Validate that the total reserved amount doesn't exceed available balance"""
        # First validate account exists and belongs to user
        account = self.account_repository.get_by_id_and_user_id(linked_account_id, user_id)
        if not account:
            raise GoalValidationError("Linked account not found or does not belong to user")
        
        # Get goals with the specific linked account using BaseRepository method
        goals = self.goal_repository.find_by(user_id=user_id, linked_account_id=linked_account_id)
        total_reserved = sum(
            float(g.linked_amount or 0)
            for g in goals
            if exclude_goal_id is None or g.id != exclude_goal_id
        )
        
        available_balance = float(account.available_balance or 0)
        total_needed = float(total_reserved) + float(linked_amount)
        
        if total_needed > available_balance:
            raise GoalValidationError(
                f"Cannot reserve more than available in the linked account (${available_balance:.2f}). "
                f"Already reserved: ${total_reserved:.2f}"
            )

    def _validate_user_exists(self, user_id: int) -> None:
        """Validate that user exists"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise GoalValidationError("User not found")

    def _validate_and_parse_deadline(self, deadline: str) -> Optional[date]:
        """Validate and parse deadline string to date object"""
        if not deadline:
            return None
        
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            if deadline_date < date.today():
                raise GoalValidationError("Deadline cannot be in the past")
            return deadline_date
        except ValueError:
            raise GoalValidationError("Invalid deadline format. Use YYYY-MM-DD")

    def _validate_and_convert_linked_fields(self, linked_account_id=None, linked_amount=None):
        """Validate and convert linked account fields"""
        if linked_account_id is not None and linked_account_id != '':
            try:
                linked_account_id = int(linked_account_id)
            except (ValueError, TypeError):
                raise GoalValidationError("linked_account_id must be an integer")
        else:
            linked_account_id = None
            
        if linked_amount is not None and linked_amount != '':
            try:
                linked_amount = float(linked_amount)
            except (ValueError, TypeError):
                raise GoalValidationError("linked_amount must be a number")
        else:
            linked_amount = None
            
        return linked_account_id, linked_amount

    def create_goal(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Create a new goal with validation"""
        # Validate user exists
        self._validate_user_exists(user_id)

        # Validate required fields
        title = kwargs.get('title', '').strip()
        if not title:
            raise GoalValidationError("Title is required")
        
        target_amount = kwargs.get('target_amount')
        if not target_amount or target_amount <= 0:
            raise GoalValidationError("Target amount must be greater than 0")

        # Parse and validate deadline
        deadline_date = self._validate_and_parse_deadline(kwargs.get('deadline'))

        # Validate category
        category = kwargs.get('category')
        if category and category not in self.VALID_CATEGORIES:
            raise GoalValidationError(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")

        # Validate and convert linked fields
        linked_account_id, linked_amount = self._validate_and_convert_linked_fields(
            kwargs.get('linked_account_id'), 
            kwargs.get('linked_amount')
        )

        # Validate linked amount total
        if linked_account_id and linked_amount is not None:
            self._validate_linked_amount_total(user_id, linked_account_id, linked_amount)

        # Prepare processed data for repository
        data = {
            'user_id': user_id,
            'title': title,
            'target_amount': target_amount,
            'description': kwargs.get('description', '').strip() or None,
            'deadline': deadline_date,
            'category': category,
            'linked_account_id': linked_account_id,
            'linked_amount': linked_amount
        }

        try:
            goal = self.goal_repository.create_goal(**data)
            return goal.to_dict()
        except Exception as e:
            raise GoalValidationError(f"Error creating goal: {str(e)}")

    def get_user_goals(self, user_id: int, status: str = None,
                      category: str = None) -> List[Dict[str, Any]]:
        """Get all goals for a user"""
        self._validate_user_exists(user_id)
        goals = self.goal_repository.get_user_goals(user_id, status, category)
        return [goal.to_dict() for goal in goals]

    def get_goal_by_id(self, goal_id: int, user_id: int) -> Dict[str, Any]:
        """Get a specific goal by ID"""
        self._validate_user_exists(user_id)
        goal = self.goal_repository.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(f"Goal with id {goal_id} not found")
        return goal.to_dict()

    def update_goal(self, goal_id: int, user_id: int, **updates) -> Dict[str, Any]:
        """Update a goal with validation"""
        # Validate user exists
        self._validate_user_exists(user_id)

        # Validate fields
        for field in updates:
            if field not in self.VALID_FIELDS:
                raise GoalValidationError(f"Invalid field: {field}")

        # Validate status if provided
        if 'status' in updates:
            if updates['status'] not in self.VALID_STATUSES:
                raise GoalValidationError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")

        # Validate target_amount if provided
        if 'target_amount' in updates:
            if updates['target_amount'] <= 0:
                raise GoalValidationError("Target amount must be greater than 0")

        # Parse deadline if provided
        if 'deadline' in updates:
            updates['deadline'] = self._validate_and_parse_deadline(updates['deadline'])

        # Validate and convert linked fields
        if 'linked_account_id' in updates or 'linked_amount' in updates:
            linked_account_id, linked_amount = self._validate_and_convert_linked_fields(
                updates.get('linked_account_id'), 
                updates.get('linked_amount')
            )
            updates['linked_account_id'] = linked_account_id
            updates['linked_amount'] = linked_amount

            # Validate linked amount total
            if linked_account_id and linked_amount is not None:
                self._validate_linked_amount_total(user_id, linked_account_id, linked_amount, exclude_goal_id=goal_id)

        try:
            goal = self.goal_repository.update_goal(goal_id, user_id, **updates)
            return goal.to_dict()
        except Exception as e:
            raise GoalValidationError(f"Error updating goal: {str(e)}")

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """Delete a goal"""
        self._validate_user_exists(user_id)
        try:
            return self.goal_repository.delete_goal(goal_id, user_id)
        except Exception as e:
            raise GoalValidationError(f"Error deleting goal: {str(e)}")

    def update_goal_progress(self, goal_id: int, user_id: int, amount: float, progress_type: str = 'manual') -> Dict[str, Any]:
        """Update goal progress by adding amount"""
        self._validate_user_exists(user_id)
        self._validate_amount(amount)
        self._validate_progress_type(progress_type)

        # Validate linked account if progress type is linked
        if progress_type == 'linked':
            goal = self.goal_repository.get_goal_by_id(goal_id, user_id)
            if not goal:
                raise GoalValidationError(f"Goal with id {goal_id} not found")
            if not goal.linked_account_id:
                raise GoalValidationError("Goal does not have a linked account")
            
            # Validate total reserved amount
            self._validate_linked_amount_total(
                user_id,
                goal.linked_account_id,
                float(goal.linked_amount or 0) + float(amount),
                exclude_goal_id=goal_id
            )

        try:
            goal = self.goal_repository.update_goal_progress(goal_id, user_id, float(amount), progress_type)
            return goal.to_dict()
        except Exception as e:
            raise GoalValidationError(f"Error updating goal progress: {str(e)}")

    def get_goals_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary statistics for user goals"""
        self._validate_user_exists(user_id)
        try:
            return self.goal_repository.get_goals_summary(user_id)
        except Exception as e:
            raise GoalValidationError(f"Error getting goals summary: {str(e)}")

    def get_overdue_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all overdue goals for a user"""
        self._validate_user_exists(user_id)
        goals = self.goal_repository.get_overdue_goals(user_id)
        return [goal.to_dict() for goal in goals]

    def get_goals_near_deadline(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get goals with deadline within specified days"""
        self._validate_user_exists(user_id)
        
        if days < 1 or days > 30:
            raise GoalValidationError("Days must be between 1 and 30")

        goals = self.goal_repository.get_goals_near_deadline(user_id, days)
        return [goal.to_dict() for goal in goals]

    def get_goals_by_category(self, user_id: int, category: str) -> List[Dict[str, Any]]:
        """Get goals filtered by category"""
        self._validate_user_exists(user_id)
        
        if category not in self.VALID_CATEGORIES:
            raise GoalValidationError(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")

        goals = self.goal_repository.get_goals_by_category(user_id, category)
        return [goal.to_dict() for goal in goals]

    def get_goal_categories(self) -> List[Dict[str, str]]:
        """Get available goal categories"""
        return [
            {'value': 'savings', 'label': 'Savings'},
            {'value': 'investment', 'label': 'Investment'},
            {'value': 'debt', 'label': 'Debt'},
            {'value': 'emergency', 'label': 'Emergency Fund'},
            {'value': 'vacation', 'label': 'Vacation'},
            {'value': 'education', 'label': 'Education'},
            {'value': 'bills', 'label': 'Bills'},
            {'value': 'other', 'label': 'Other'}
        ]

    def search_goals(self, user_id: int, search_term: str = None, 
                    status: str = None, category: str = None,
                    min_amount: float = None, max_amount: float = None) -> List[Dict[str, Any]]:
        """Search goals with multiple filters"""
        self._validate_user_exists(user_id)
        
        # Validate status if provided
        if status and status not in self.VALID_STATUSES:
            raise GoalValidationError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
        
        # Validate category if provided
        if category and category not in self.VALID_CATEGORIES:
            raise GoalValidationError(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")
        
        # Validate amount ranges
        if min_amount is not None and min_amount < 0:
            raise GoalValidationError("Minimum amount cannot be negative")
        if max_amount is not None and max_amount < 0:
            raise GoalValidationError("Maximum amount cannot be negative")
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise GoalValidationError("Minimum amount cannot be greater than maximum amount")
        
        # Prepare search parameters
        search_params = {
            'user_id': user_id,
            'search_term': search_term,
            'status': status,
            'category': category,
            'min_amount': min_amount,
            'max_amount': max_amount
        }
        
        goals = self.goal_repository.search_goals(**search_params)
        return [goal.to_dict() for goal in goals]

    def get_goals_with_accounts(self, user_id: int, status: str = None, 
                              category: str = None) -> List[Dict[str, Any]]:
        """Get goals with linked account information loaded"""
        self._validate_user_exists(user_id)
        goals = self.goal_repository.get_user_goals_with_accounts(user_id, status, category)
        return [goal.to_dict() for goal in goals]

    def validate_goal_permissions(self, goal_id: int, user_id: int) -> bool:
        """Validate that user has permission to access the goal"""
        self._validate_user_exists(user_id)
        goal = self.goal_repository.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(f"Goal with id {goal_id} not found")
        return True

    def get_goal_progress(self, goal_id: int, user_id: int) -> Dict[str, Any]:
        """Get goal progress information"""
        self.validate_goal_permissions(goal_id, user_id)
        goal = self.goal_repository.get_goal_by_id(goal_id, user_id)
        
        progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining_amount = goal.target_amount - goal.current_amount
        
        return {
            'goal_id': goal.id,
            'current_amount': goal.current_amount,
            'target_amount': goal.target_amount,
            'progress_percentage': progress_percentage,
            'remaining_amount': remaining_amount,
            'is_completed': goal.current_amount >= goal.target_amount
        }

    def get_goals_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed statistics for user goals"""
        self._validate_user_exists(user_id)
        
        # Get basic summary
        summary = self.goal_repository.get_goals_summary(user_id)
        
        # Get goals by category
        category_stats = {}
        for category in self.VALID_CATEGORIES:
            goals = self.goal_repository.get_goals_by_category(user_id, category)
            category_stats[category] = {
                'count': len(goals),
                'total_target': sum(float(g.target_amount) for g in goals),
                'total_current': sum(float(g.current_amount) for g in goals),
                'completed': len([g for g in goals if g.status == 'completed'])
            }
        
        # Get goals by status
        status_stats = {}
        for status in self.VALID_STATUSES:
            goals = self.goal_repository.find_by(user_id=user_id, status=status)
            status_stats[status] = {
                'count': len(goals),
                'total_target': sum(float(g.target_amount) for g in goals),
                'total_current': sum(float(g.current_amount) for g in goals)
            }
        
        return {
            'summary': summary,
            'by_category': category_stats,
            'by_status': status_stats
        }

    def _validate_progress_type(self, progress_type: str) -> None:
        """Validate progress type"""
        valid_types = ['manual', 'linked']
        if progress_type not in valid_types:
            raise GoalValidationError(f"Invalid progress type. Must be one of: {', '.join(valid_types)}")

    def _validate_amount(self, amount: float) -> None:
        """Validate amount is positive"""
        if amount <= 0:
            raise GoalValidationError("Amount must be greater than 0") 