from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions.database import db


class Goal(db.Model):
    """Goal model for user financial goals"""
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_amount = Column(Numeric(10, 2), nullable=False)
    current_amount = Column(Numeric(10, 2), default=0)
    deadline = Column(Date)
    category = Column(String(50))
    status = Column(String(20), default='active')  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Nuevos campos para cuenta asociada
    linked_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    linked_amount = Column(Numeric(10, 2), nullable=True)

    # Relationships
    user = relationship('User', back_populates='goals')
    linked_account = relationship('Account', foreign_keys=[linked_account_id])

    def __init__(self, user_id, title, target_amount, description=None, deadline=None, category=None, linked_account_id=None, linked_amount=None):
        self.user_id = user_id
        self.title = title
        self.target_amount = target_amount
        self.description = description
        self.deadline = deadline
        self.category = category
        self.status = 'active'
        self.current_amount = 0
        self.linked_account_id = linked_account_id
        self.linked_amount = linked_amount

    def to_dict(self):
        """Convert goal to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'category': self.category,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'progress_percentage': self.calculate_progress(),
            'days_remaining': self.calculate_days_remaining(),
            'linked_account_id': self.linked_account_id,
            'linked_amount': float(self.linked_amount) if self.linked_amount is not None else None,
            'linked_account': self.linked_account.to_dict() if self.linked_account else None
        }

    def calculate_progress(self):
        """Calculate progress percentage, including linked_amount if present"""
        total = float(self.current_amount or 0)
        if self.linked_amount:
            total += float(self.linked_amount)
        if self.target_amount == 0:
            return 0
        progress = (total / float(self.target_amount)) * 100
        return min(progress, 100)

    def calculate_days_remaining(self):
        """Calculate days remaining until deadline"""
        if not self.deadline:
            return None
        remaining = self.deadline - datetime.now().date()
        return remaining.days

    def update_progress(self, amount, progress_type='manual'):
        if progress_type == 'linked':
            self.linked_amount = float(self.linked_amount or 0) + float(amount)
        else:
            self.current_amount = float(self.current_amount or 0) + float(amount)
        if self.calculate_progress() >= 100:
            self.status = 'completed'
        self.updated_at = datetime.utcnow()

    def is_overdue(self):
        """Check if goal is overdue"""
        if not self.deadline:
            return False
        return datetime.now().date() > self.deadline and self.status == 'active' 