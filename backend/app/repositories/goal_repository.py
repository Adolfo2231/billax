from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func, case, cast, Float
from app.models.goal import Goal
from app.repositories.base_repository import BaseRepository
from app.utils.goal_exceptions import GoalNotFoundError, GoalValidationError


class GoalRepository(BaseRepository[Goal]):
    """Repository for Goal model operations"""

    def __init__(self):
        super().__init__()
        self.model = Goal

    def create_goal(self, **kwargs) -> Goal:
        """Create a new goal for a user"""
        try:
            return self.create(**kwargs)
        except Exception as e:
            raise GoalValidationError(f"Error creating goal: {str(e)}")

    def get_user_goals(self, user_id: int, status: str = None, 
                      category: str = None) -> List[Goal]:
        """Get all goals for a user with optional filters"""
        query = self.db.session.query(Goal).filter(Goal.user_id == user_id)
        
        if status:
            query = query.filter(Goal.status == status)
        
        if category:
            query = query.filter(Goal.category == category)
        
        return query.order_by(Goal.created_at.desc()).all()

    def search_goals(self, user_id: int, search_term: str = None, 
                    status: str = None, category: str = None,
                    min_amount: float = None, max_amount: float = None) -> List[Goal]:
        """Search goals with multiple filters"""
        query = self.db.session.query(Goal).filter(Goal.user_id == user_id)
        
        if search_term:
            search_filter = or_(
                Goal.title.ilike(f'%{search_term}%'),
                Goal.description.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        if status:
            query = query.filter(Goal.status == status)
        
        if category:
            query = query.filter(Goal.category == category)
        
        if min_amount is not None:
            query = query.filter(Goal.target_amount >= min_amount)
        
        if max_amount is not None:
            query = query.filter(Goal.target_amount <= max_amount)
        
        return query.order_by(Goal.created_at.desc()).all()

    def get_goal_by_id(self, goal_id: int, user_id: int) -> Optional[Goal]:
        """Get a specific goal by ID for a user"""
        return self.find_one_by(id=goal_id, user_id=user_id)

    def update_goal(self, goal_id: int, user_id: int, **updates) -> Goal:
        """Update a goal"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(f"Goal with id {goal_id} not found")
        
        try:
            return self.update(goal, **updates)
        except Exception as e:
            raise GoalValidationError(f"Error updating goal: {str(e)}")

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """Delete a goal"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(f"Goal with id {goal_id} not found")
        
        try:
            return self.delete(goal)
        except Exception as e:
            raise GoalValidationError(f"Error deleting goal: {str(e)}")

    def update_goal_progress(self, goal_id: int, user_id: int, amount: float, progress_type: str = 'manual') -> Goal:
        """Update goal progress by adding amount to current_amount or linked_amount"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise GoalNotFoundError(f"Goal with id {goal_id} not found")
        try:
            goal.update_progress(amount, progress_type)
            self.db.session.commit()
            return goal
        except Exception as e:
            self.db.session.rollback()
            raise GoalValidationError(f"Error updating goal progress: {str(e)}")

    def get_goals_by_category(self, user_id: int, category: str) -> List[Goal]:
        """Get goals filtered by category"""
        goals = self.find_by(user_id=user_id, category=category)
        return sorted(goals, key=lambda x: x.created_at, reverse=True)

    def get_active_goals(self, user_id: int) -> List[Goal]:
        """Get all active goals for a user"""
        goals = self.find_by(user_id=user_id, status='active')
        return sorted(goals, key=lambda x: x.created_at, reverse=True)

    def get_completed_goals(self, user_id: int) -> List[Goal]:
        """Get all completed goals for a user"""
        goals = self.find_by(user_id=user_id, status='completed')
        return sorted(goals, key=lambda x: x.created_at, reverse=True)

    def get_overdue_goals(self, user_id: int) -> List[Goal]:
        """Get all overdue goals for a user"""
        today = date.today()
        return self.db.session.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == 'active',
                Goal.deadline < today
            )
        ).all()

    def get_goals_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary statistics for user goals using optimized SQL queries"""
        # Use SQL aggregation for better performance
        summary_query = self.db.session.query(
            func.count(Goal.id).label('total_goals'),
            func.sum(case((Goal.status == 'active', 1), else_=0)).label('active_goals'),
            func.sum(case((Goal.status == 'completed', 1), else_=0)).label('completed_goals'),
            func.sum(cast(Goal.target_amount, Float)).label('total_target_amount'),
            func.sum(cast(Goal.current_amount, Float)).label('total_current_amount')
        ).filter(Goal.user_id == user_id).first()
        
        # Get overdue goals count separately
        overdue_count = self.db.session.query(func.count(Goal.id)).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == 'active',
                Goal.deadline < date.today()
            )
        ).scalar()
        
        total_target = float(summary_query.total_target_amount or 0)
        total_current = float(summary_query.total_current_amount or 0)
        
        return {
            'total_goals': summary_query.total_goals or 0,
            'active_goals': summary_query.active_goals or 0,
            'completed_goals': summary_query.completed_goals or 0,
            'overdue_goals': overdue_count or 0,
            'total_target_amount': total_target,
            'total_current_amount': total_current,
            'overall_progress': (total_current / total_target * 100) if total_target > 0 else 0
        }

    def get_goals_near_deadline(self, user_id: int, days: int = 7) -> List[Goal]:
        """Get goals with deadline within specified days"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return self.db.session.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == 'active',
                Goal.deadline >= today,
                Goal.deadline <= future_date
            )
        ).order_by(Goal.deadline.asc()).all()

    def get_user_goals_with_accounts(self, user_id: int, status: str = None, 
                                   category: str = None) -> List[Goal]:
        """Get all goals for a user with linked accounts loaded to avoid N+1 queries"""
        filters = {'user_id': user_id}
        if status:
            filters['status'] = status
        if category:
            filters['category'] = category
        
        goals = self.find_by(**filters)
        return sorted(goals, key=lambda x: x.created_at, reverse=True) 