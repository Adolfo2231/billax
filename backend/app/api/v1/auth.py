"""
Authentication API endpoints for user registration, login, and password management.

This module provides RESTful endpoints for user authentication, including:
- User registration with validation
- User login with JWT token generation
- Password recovery and reset
- Password change for authenticated users
"""

from flask_restx import Namespace, fields, Resource
from app.facade.auth_facade import AuthFacade
from typing import Dict, Any
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create the authentication namespace
auth_ns = Namespace("auth", description="User registration and authentication")

# Create facade instance
auth_facade = AuthFacade()

# Define request/response models
register_model = auth_ns.model("Register", {
    "first_name": fields.String(required=True, example="John", description="First name (only letters, spaces, apostrophes, and hyphens allowed)"),
    "last_name": fields.String(required=True, example="Doe", description="Last name (only letters, spaces, apostrophes, and hyphens allowed)"),
    "email": fields.String(required=True, example="john@example.com", description="Valid email address"),
    "password": fields.String(required=True, example="secure123", description="Password (minimum 6 characters)"),
    "role": fields.String(required=False, example="User", description="Role of the user (default: User)")
})

token_model = auth_ns.model("Token", {
    "message": fields.String(example="Login successful"),
    "token": fields.String,
    "user": fields.Nested(auth_ns.model("User", {
        "id": fields.String,
        "name": fields.String,
        "email": fields.String
    }))
})

register_response_model = auth_ns.model("RegisterResponse", {
    "message": fields.String(example="User registered successfully"),
    "user": fields.Nested(auth_ns.model("User", {
        "id": fields.String,
        "name": fields.String,
        "email": fields.String
    }))
})

error_model = auth_ns.model("Error", {
    "error": fields.String(example="Invalid credentials"),
    "message": fields.String(example="The provided credentials are invalid")
})

login_model = auth_ns.model("Login", {
    "email": fields.String(required=True, example="john@example.com", description="User's email address"),
    "password": fields.String(required=True, example="secure123", description="User's password")
})

forgot_password_model = auth_ns.model("ForgotPassword", {
    "email": fields.String(required=True, example="john@example.com", description="Email address to send reset link")
})

reset_password_model = auth_ns.model("ResetPassword", {
    "token": fields.String(required=True, description="Password reset token from email"),
    "new_password": fields.String(required=True, example="newSecurePass123", description="New password")
})

@auth_ns.route("/register")
class Register(Resource):
    """
    Endpoint for user registration.
    
    This endpoint handles new user registration with validation of:
    - Required fields (name, email, password)
    - Email format
    - Password length
    - Name format (letters, spaces, apostrophes, hyphens only)
    """

    @auth_ns.doc('register')
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.response(201, "User registered", register_response_model)
    @auth_ns.response(400, "Validation error", error_model)
    @auth_ns.response(404, "User not found", error_model)
    @auth_ns.response(500, "Internal server error", error_model)
    @handle_errors
    def post(self) -> Dict[str, Any]:
        """
        Register a new user.

        This endpoint validates the registration data and creates a new user.
        The user must then login to obtain an access token.

        Args:
            Request body (JSON):
                - name (str): User's full name
                - email (str): User's email address
                - password (str): User's password
                - role (str): User's role (default: User)

        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - token (str): JWT token for authentication
                - user (dict): User information
                - status_code (int): 201 for success

        Raises:
            HTTP 400: If validation fails (invalid email, password, or duplicate email)
            HTTP 500: For server errors

        Example:
            >>> response = client.post('/api/v1/auth/register', json={
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com',
            ...     'password': 'secure123'
            ... })
            >>> print(response.status_code)
            201
            >>> print(response.json['message'])
            User registered successfully
        """
        data = auth_ns.payload
        return auth_facade.register_user(data), 201

@auth_ns.route("/login")
class Login(Resource):
    """
    Endpoint for user login.
    
    This endpoint handles user authentication and returns a JWT token
    that can be used for subsequent authenticated requests.
    """
    
    @auth_ns.doc('login')
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, "Login successful", token_model)
    @auth_ns.response(401, "Invalid credentials", error_model)
    @auth_ns.response(500, "Internal server error", error_model)
    @handle_errors
    def post(self) -> Dict[str, Any]:
        """
        Authenticate a user and return a JWT token.
        
        This endpoint validates the user credentials and, if valid,
        generates and returns a JWT token for authentication.
        
        Args:
            Request body (JSON):
                - email (str): User's email address
                - password (str): User's password
                
        Returns:
            Dict[str, Any]: Response containing:
                - message (str): Success message
                - token (str): JWT token for authentication
                - user (dict): Basic user information
                
        Raises:
            HTTP 401: If credentials are invalid
            HTTP 500: For server errors
        """
        data = auth_ns.payload
        return auth_facade.login_user(data)

@auth_ns.route("/forgot-password")
class ForgotPassword(Resource):
    """Endpoint for initiating password recovery process."""
    
    @auth_ns.doc('forgot_password')
    @auth_ns.expect(forgot_password_model, validate=True)
    @auth_ns.response(200, "Reset email sent")
    @auth_ns.response(404, "Email not found", error_model)
    @auth_ns.response(500, "Internal server error", error_model)
    @handle_errors
    def post(self) -> Dict[str, str]:
        """
        Request a password reset link.
        
        Sends an email with a password reset token if the email exists in the system.
        """
        data = auth_ns.payload
        auth_facade.request_password_reset(data["email"])
        return {"message": "If the email exists in our system, you will receive a password reset link"}

@auth_ns.route("/reset-password")
class ResetPassword(Resource):
    """Endpoint for resetting password using token from email."""
    
    @auth_ns.doc('reset_password')
    @auth_ns.expect(reset_password_model, validate=True)
    @auth_ns.response(200, "Password reset successful")
    @auth_ns.response(400, "Invalid token", error_model)
    @auth_ns.response(500, "Internal server error", error_model)
    @handle_errors
    def post(self) -> Dict[str, str]:
        """
        Reset password using token.
        
        Validates the token and updates the user's password.
        """
        data = auth_ns.payload
        auth_facade.reset_password(data["token"], data["new_password"])
        return {"message": "Password updated successfully"}