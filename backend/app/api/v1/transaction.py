from flask_restx import Namespace, Resource, fields, reqparse
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.facade.transation_facade import TransactionFacade
import datetime

transaction_ns = Namespace("transaction", description="Transaction API endpoints")

transaction_facade = TransactionFacade()

transaction_model = transaction_ns.model("Transaction", {
    "id": fields.Integer(required=True, description="Transaction ID"),
    "amount": fields.Float(required=True, description="Transaction amount"),
    "date": fields.DateTime(required=True, description="Transaction date"),
    "description": fields.String(required=True, description="Transaction description"),
})

error_model = transaction_ns.model("Error", {
    "message": fields.String(required=True, description="Error message"),
})

@transaction_ns.route("/transactions")
class Transactions(Resource):
    @transaction_ns.doc("get_transactions")
    @transaction_ns.response(200, "Transactions retrieved successfully")
    @transaction_ns.response(400, "Validation error", error_model)
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False, help='Number of transactions to retrieve')
        parser.add_argument('offset', type=int, required=False, default=0, help='Offset for pagination')
        parser.add_argument('start_date', type=str, required=False, help='Start date in YYYY-MM-DD format')
        parser.add_argument('end_date', type=str, required=False, help='End date in YYYY-MM-DD format')
        args = parser.parse_args()
        
        user_id = get_jwt_identity()
        result = transaction_facade.get_user_transactions(
            user_id,
            args.get('limit'),
            args.get('offset'),
            args.get('start_date'),
            args.get('end_date')
        )
        return result

@transaction_ns.route("/sync-transactions")
class SyncTransactions(Resource):
    @transaction_ns.doc("sync_transactions")
    @transaction_ns.response(200, "Transactions synced successfully", transaction_model)
    @transaction_ns.response(400, "Validation error", error_model)
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', type=str, required=False, help='Start date in YYYY-MM-DD format')
        parser.add_argument('end_date', type=str, required=False, help='End date in YYYY-MM-DD format')
        parser.add_argument('count', type=int, required=False, help='Number of transactions to retrieve (optional, gets all if not specified)')
        args = parser.parse_args()
        
        user_id = get_jwt_identity()
        result = transaction_facade.sync_transactions(user_id, args.get('start_date'), args.get('end_date'), args.get('count'))
        return result
    
@transaction_ns.route("/by-type/<string:transaction_type>")
class TransactionsByType(Resource):
    @transaction_ns.doc("get_transactions_by_type")
    @transaction_ns.response(200, "Transactions retrieved successfully", transaction_model)
    @transaction_ns.response(404, "Transactions not found", error_model)
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self, transaction_type):
        user_id = get_jwt_identity()
        result = transaction_facade.get_transactions_by_type(user_id, transaction_type)
        return result

@transaction_ns.route("/<int:transaction_id>")
class Transaction(Resource):
    @transaction_ns.doc("get_transaction")
    @transaction_ns.response(200, "Transaction retrieved successfully", transaction_model)
    @transaction_ns.response(404, "Transaction not found", error_model)
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self, transaction_id):
        user_id = get_jwt_identity()
        result = transaction_facade.get_transaction_by_id(user_id, transaction_id)
        return result

@transaction_ns.route("/summary")
class TransactionSummary(Resource):
    @transaction_ns.doc("get_transaction_summary")
    @transaction_ns.response(200, "Transaction summary retrieved successfully")
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        result = transaction_facade.get_transaction_summary(user_id)
        return result

@transaction_ns.route("/<int:transaction_id>/delete")
class DeleteTransaction(Resource):
    @transaction_ns.doc("delete_transaction")
    @transaction_ns.response(200, "Transaction deleted successfully")
    @transaction_ns.response(404, "Transaction not found", error_model)
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def delete(self, transaction_id):
        user_id = get_jwt_identity()
        result = transaction_facade.delete_transaction(user_id, transaction_id)
        return result
    
@transaction_ns.route("/delete-all")
class DeleteAllTransactions(Resource):
    @transaction_ns.doc("delete_all_transactions")
    @transaction_ns.response(200, "All transactions deleted successfully")
    @transaction_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        result = transaction_facade.delete_all_transactions(user_id)
        return result