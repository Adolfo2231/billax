"""
API v1 initialization module.

This module initializes the API v1 blueprint and registers all namespaces.
"""

from flask import Blueprint
from flask_restx import Api
from app.api.v1.auth import auth_ns


# Create the API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Create the API instance
api = Api(
    api_v1_bp,
    version='1.0',
    title='Billax API',
    description='Billax Financial Management API',
    doc='/docs',
)

# Register all namespaces
api.add_namespace(auth_ns, path='/auth')