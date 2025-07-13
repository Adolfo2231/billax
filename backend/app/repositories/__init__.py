"""
Repository module exports.

This module exports the main repository classes and interfaces
for easy importing throughout the application.
"""

from .base_repository import IRepository, BaseRepository
from .goal_repository import GoalRepository

__all__ = [
    'IRepository',
    'BaseRepository', 
    'GoalRepository'
] 