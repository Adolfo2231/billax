"""
User Management API endpoints for profile operations.

This module provides REST API endpoints for user profile management and operations.
It handles authenticated user profile retrieval and updates, with proper JWT token
validation and error handling. The endpoints are part of the v1 API namespace and
use Flask-RESTX for request/response modeling and documentation.

Key Features:
- Authenticated user profile retrieval
- JWT token validation
- Error handling and status codes
- Profile data serialization

Example:
    >>> # Get authenticated user's profile
    >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
    >>> response = client.get('/api/v1/users/me', headers=headers)
    >>> print(response.status_code)
    200
    >>> print(response.json)
    {
        'id': 'user-123',
        'name': 'John Doe',
        'email': 'john@example.com'
    }
"""

from typing import Dict, Any, Tuple
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.facade.user_facade import UserFacade

# Create the users namespace
user_ns = Namespace("users", description="User operations")

# Define response model for user data
user_model = user_ns.model("User", {
    "id": fields.String(description="User UUID"),
    "name": fields.String(description="User's full name"),
    "email": fields.String(description="User's email address")
})


@user_ns.route("/me")
class UserMe(Resource):
    """
    Resource for authenticated user profile operations.

    This endpoint provides access to the authenticated user's profile information.
    It requires a valid JWT token in the Authorization header and returns the
    user's profile data upon successful authentication.
    """

    @user_ns.doc(security="Bearer")
    @user_ns.response(200, "Success", user_model)
    @user_ns.response(401, "Unauthorized")
    @user_ns.response(404, "User not found")
    @jwt_required()
    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        Get the authenticated user's profile information.

        This endpoint retrieves the profile information of the currently
        authenticated user based on the JWT token in the Authorization header.

        Args:
            Headers:
                - Authorization: Bearer <jwt_token>

        Returns:
            Tuple[Dict[str, Any], int]: Response containing:
                - user_data (dict): User profile information
                    - id (str): User's UUID
                    - name (str): User's full name
                    - email (str): User's email address
                - status_code (int): 200 for success

        Raises:
            HTTP 401: If no valid JWT token is provided
            HTTP 404: If the user is not found in the database

        Example:
            >>> headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
            >>> response = client.get('/api/v1/users/me', headers=headers)
            >>> print(response.status_code)
            200
            >>> print(response.json)
            {
                'id': 'user-123',
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        """
        user_id = get_jwt_identity()
        user = UserFacade.get_user_by_id(user_id)
        
        if not user:
            return {"message": "User not found"}, 404
            
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }, 200