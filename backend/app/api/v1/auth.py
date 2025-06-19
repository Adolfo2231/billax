"""
Authentication API endpoints for user registration, login, and logout.

This module provides RESTful endpoints for user authentication, including:
- User registration with validation
- User login with JWT token generation
- User logout with token invalidation

The endpoints use Flask-RESTX for request parsing, validation, and documentation.
"""

from flask_restx import Namespace, fields
from app.facade.auth_facade import AuthFacade
from flask_restx import Resource
from typing import Dict, Any
from app.utils.decorators.error_handler import handle_errors


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