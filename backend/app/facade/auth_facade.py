"""
auth_facade.py

This module defines the AuthFacade class that orchestrates authentication operations.
It acts as an intermediary between the API layer and the repository layer.
"""

from typing import Dict, Any
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.extensions.jwt import create_token, create_access_token, blacklist_token
from app.extensions.mail import send_password_reset_email
from werkzeug.security import check_password_hash
from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token, decode_token


class AuthFacade:
    """
    Facade for authentication operations.
    
    This class orchestrates user registration and authentication operations by coordinating 
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
        
        user = User(**data)
        user = self.user_repository.save(user)
        return user.to_dict()
        
    def login_user(self, data: dict) -> Dict[str, Any]:
        """
        Authenticate a user and generate a JWT token.
        
        Args:
            data (dict): Login data including email and password.
            
        Returns:
            Dict[str, Any]: Response containing token and user data.
            
        Raises:
            ValueError: If credentials are invalid.
        """
        email = data["email"]
        password = data["password"]
        
        # Get user by email
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
            
        # Verify password
        if not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")
            
        # Generate token using flask_jwt_extended
        token = create_token(str(user.id))
        
        return {
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }

    def request_password_reset(self, email: str) -> None:
        """
        Request a password reset for a user.
        
        Args:
            email (str): Email address of the user requesting reset
            
        Note:
            This method intentionally does not raise errors for non-existent emails
            to prevent email enumeration attacks.
        """
        user = self.user_repository.get_by_email(email)
        if user:
            # Create a reset token valid for 1 hour
            reset_token = create_access_token(
                identity=str(user.id),
                additional_claims={'type': 'reset'},
                expires_delta=timedelta(hours=1)
            )
            # For testing: print token to console instead of sending email
            print(f"\n=== PASSWORD RESET TOKEN FOR {email} ===")
            print(f"Token: {reset_token}")
            print(f"Reset URL: http://localhost:3000/reset-password?token={reset_token}")
            print("==========================================\n")
            
            # Uncomment the line below when email is properly configured
            # send_password_reset_email(email, reset_token)

    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset a user's password using a reset token.
        
        Args:
            token (str): The reset token from the email
            new_password (str): The new password to set
            
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Verify and decode token
            decoded = decode_token(token)
            
            # Verify it's a reset token (check at root level)
            if decoded.get('type') != 'reset':
                raise ValueError("Invalid reset token")
                
            # Get user (convert string back to int for database lookup)
            user = self.user_repository.get_by_id(int(decoded['sub']))
            if not user:
                raise ValueError("User not found")
                
            # Update password
            user.set_password(new_password)
            self.user_repository.save(user)
            
        except Exception as e:
            raise ValueError("Invalid or expired reset token")

    def logout_user(self, token: str) -> None:
        """
        Logout a user by blacklisting their token.
        
        Args:
            token (str): The JWT token to blacklist
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Decode the token to get JTI and expiration
            decoded = decode_token(token)
            jti = decoded['jti']
            user_id = int(decoded['sub'])
            expires_at = datetime.fromtimestamp(decoded['exp'])
            
            # Add token to blacklist
            blacklist_token(jti, user_id, expires_at)
            
        except Exception as e:
            raise ValueError("Invalid token")