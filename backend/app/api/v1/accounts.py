from flask_restx import Namespace, fields, Resource
from app.facade.accounts_facade import AccountsFacade
from typing import Dict, Any
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create the accounts namespace
accounts_ns = Namespace("accounts", description="Accounts API endpoints")

# Create facade instance
accounts_facade = AccountsFacade()

# Define models
account_model = accounts_ns.model("Account", {
    "account_id": fields.String(description="Plaid account ID"),
    "name": fields.String(description="Account name"),
    "type": fields.String(description="Account type"),
    "subtype": fields.String(description="Account subtype"),
    "balances": fields.Raw(description="Account balances"),
    "mask": fields.String(description="Account number mask")
})

accounts_response_model = accounts_ns.model("AccountsResponse", {
    "accounts": fields.List(fields.Nested(account_model), description="List of user accounts")
})

error_model = accounts_ns.model("Error", {
    "error": fields.String(required=True, description="Error message"),
    "message": fields.String(required=True, description="Error message")
})

@accounts_ns.route("/")
class Accounts(Resource):
    @accounts_ns.doc("get_accounts")
    @accounts_ns.response(200, "Accounts retrieved successfully", accounts_response_model)
    @accounts_ns.response(400, "User not linked to Plaid", error_model)
    @accounts_ns.response(404, "User not found", error_model)
    @accounts_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        accounts = accounts_facade.get_accounts(user_id)
        return {"accounts": accounts}
    
@accounts_ns.route("/<int:account_id>")
class Account(Resource):
    @accounts_ns.doc("get_account")
    @accounts_ns.response(200, "Account retrieved successfully", account_model)
    @accounts_ns.response(404, "Account not found", error_model)
    @accounts_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self, account_id):
        user_id = get_jwt_identity()
        account = accounts_facade.get_account_by_id(user_id, account_id)
        return account