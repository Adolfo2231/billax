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

# Define summary models
account_type_summary_model = accounts_ns.model("AccountTypeSummary", {
    "count": fields.Integer(description="Number of accounts of this type"),
    "total_balance": fields.Float(description="Total balance for this account type")
})

account_status_summary_model = accounts_ns.model("AccountStatusSummary", {
    "count": fields.Integer(description="Number of accounts with this status"),
    "total_balance": fields.Float(description="Total balance for this status")
})

balance_trend_model = accounts_ns.model("BalanceTrend", {
    "available": fields.Float(description="Total available balance"),
    "current": fields.Float(description="Total current balance"),
    "limit": fields.Float(description="Total credit limit")
})

accounts_summary_model = accounts_ns.model("AccountsSummary", {
    "total_accounts": fields.Integer(description="Total number of accounts"),
    "total_balance": fields.Float(description="Total balance across all accounts"),
    "accounts_by_type": fields.Raw(description="Summary grouped by account type"),
    "accounts_by_status": fields.Raw(description="Summary grouped by account status"),
    "balance_trend": fields.Nested(balance_trend_model, description="Balance trend information")
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
    
@accounts_ns.route("/<string:account_type>")
class AccountsByType(Resource):
    @accounts_ns.doc("get_accounts_by_type")
    @accounts_ns.response(200, "Accounts retrieved successfully", accounts_response_model)
    @accounts_ns.response(404, "Accounts not found", error_model)
    @accounts_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self, account_type):
        user_id = get_jwt_identity()
        accounts = accounts_facade.get_accounts_by_type(user_id, account_type)
        return {"accounts": accounts}
    
@accounts_ns.route("/")
class DeleteAccounts(Resource):
    @accounts_ns.doc("delete_accounts")
    @accounts_ns.response(200, "Accounts deleted successfully", error_model)
    @accounts_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        accounts_facade.delete_accounts(user_id)
        return {"message": "Accounts deleted successfully"}
    
@accounts_ns.route("/summary")
class AccountsSummary(Resource):
    @accounts_ns.doc("get_accounts_summary")
    @accounts_ns.response(200, "Accounts summary retrieved successfully", accounts_summary_model)
    @accounts_ns.response(404, "Accounts not found", error_model)
    @accounts_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        summary = accounts_facade.get_accounts_summary(user_id)
        return {"summary": summary}