"""
Authentication API endpoints for user registration and login.

This module provides REST API endpoints for user authentication using JWT tokens.
It handles user registration and login operations, with proper validation and
error handling. The endpoints are part of the v1 API namespace and use Flask-RESTX
for request/response modeling and documentation.

Key Features:
- User registration with validation
- JWT token generation
- Secure password handling
- Error handling and status codes

Example:
    >>> # Register a new user
    >>> response = client.post('/api/v1/auth/register', json={
    ...     'name': 'John Doe',
    ...     'email': 'john@example.com',
    ...     'password': 'secure123'
    ... })
    >>> print(response.status_code)
    201
    >>> print(response.json['access_token'])
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
"""

from typing import Dict, Any, Tuple
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.facade.user_facade import UserFacade
from app.exceptions.exceptions import (
    InvalidEmailError,
    InvalidPasswordError,
    InvalidNameError,
    DuplicateEmailError
)

# Create the authentication namespace
auth_ns = Namespace("auth", description="User registration and authentication")

# Define request/response models
register_model = auth_ns.model("Register", {
    "name": fields.String(required=True, example="John Doe"),
    "email": fields.String(required=True, example="john@example.com"),
    "password": fields.String(required=True, example="secure123")
})

login_model = auth_ns.model("Login", {
    "email": fields.String(required=True, example="user@example.com"),
    "password": fields.String(required=True, example="mypassword")
})

token_model = auth_ns.model("Token", {
    "access_token": fields.String
})


@auth_ns.route("/register")
class Register(Resource):
    """
    Resource for user registration.

    This endpoint handles new user registration, validates the input data,
    creates the user in the database, and returns a JWT access token.
    """

    @auth_ns.expect(register_model, validate=True)
    @auth_ns.response(201, "User registered", token_model)
    @auth_ns.response(400, "Validation error")
    def post(self) -> Tuple[Dict[str, str], int]:
        """
        Register a new user and return a JWT token.

        This endpoint validates the registration data, creates a new user,
        and returns a JWT access token for immediate authentication.

        Args:
            Request body (JSON):
                - name (str): User's full name
                - email (str): User's email address
                - password (str): User's password

        Returns:
            Tuple[Dict[str, str], int]: Response containing:
                - access_token (str): JWT token for authentication
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
            >>> print(response.json['access_token'])
            eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        """
        data = request.json
        try:
            user = UserFacade.create_user(
                name=data["name"],
                email=data["email"],
                password=data["password"]
            )
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 201

        except (InvalidEmailError, InvalidPasswordError, InvalidNameError, DuplicateEmailError) as e:
            return {"message": str(e)}, 400


@auth_ns.route("/login")
class Login(Resource):
    """
    Resource for user login.

    This endpoint handles user authentication, verifies credentials,
    and returns a JWT access token upon successful login.
    """

    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, "Login successful", token_model)
    @auth_ns.response(401, "Invalid email or password")
    def post(self) -> Tuple[Dict[str, str], int]:
        """
        Authenticate a user and return a JWT token.

        This endpoint validates the login credentials and returns a JWT
        access token if the authentication is successful.

        Args:
            Request body (JSON):
                - email (str): User's email address
                - password (str): User's password

        Returns:
            Tuple[Dict[str, str], int]: Response containing:
                - access_token (str): JWT token for authentication
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If credentials are invalid
            HTTP 500: For server errors

        Example:
            >>> response = client.post('/api/v1/auth/login', json={
            ...     'email': 'john@example.com',
            ...     'password': 'secure123'
            ... })
            >>> print(response.status_code)
            200
            >>> print(response.json['access_token'])
            eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        """
        data = request.json
        email = data["email"]
        password = data["password"]

        user = UserFacade.get_user_by_email(email)
        if not user or not user.check_password(password):
            return {"message": "Invalid email or password"}, 401

        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200
