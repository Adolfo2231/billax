"""
auth_facade.py

This module defines the AuthFacade class that orchestrates authentication operations.
It acts as an intermediary between the API layer and the repository layer.
"""

from typing import Dict, Any
from app.repositories.user_repository import UserRepository
from app.models.user import User


class AuthFacade:
    """
    Facade for authentication operations.
    
    This class orchestrates user registration operations by coordinating 
    between the API and repository layers.
    
    Attributes:
        user_repository (UserRepository): Repository for user operations.
    """
    
    def __init__(self):
        """
        Initialize the auth facade.
        
        Args:
            user_repository (UserRepository): Repository for user operations.
        """
        self.user_repository = UserRepository()
    
    def register_user(self, data: dict) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            data (dict): User data including email, password, first_name, last_name, role.
            
        Returns:
            Dict[str, Any]: User data without sensitive information.
            
        Raises:
            ValueError: If email already exists or validation fails.
        """
        email = data["email"]
        
        # Check if email already exists
        if self.user_repository.exists_by_email(email):
            raise ValueError("Email already exists")
        
        # Create user instance (validation and hashing happen in User constructor)
        user = User(**data)
        
        # Save user to database
        user = self.user_repository.save(user)
        
        return user.to_dict()