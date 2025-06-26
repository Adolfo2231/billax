"""
API v1 initialization module.

This module initializes the API v1 blueprint and registers all namespaces.
"""

from flask import Blueprint
from flask_restx import Api
from app.api.v1.auth import auth_ns
from app.api.v1.plaid import plaid_ns
from app.api.v1.accounts import accounts_ns
from app.api.v1.transaction import transaction_ns
from app.api.v1.chat import chat_ns

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
api.add_namespace(plaid_ns, path='/plaid')
api.add_namespace(accounts_ns, path='/accounts')
api.add_namespace(transaction_ns, path='/transaction')
api.add_namespace(chat_ns, path='/chat')