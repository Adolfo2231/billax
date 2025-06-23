from flask_restx import Namespace, Resource, fields
from app.facade.plaid_facade import PlaidFacade
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

plaid_ns = Namespace("plaid", description="Plaid API endpoints")

link_token_model = plaid_ns.model("LinkToken", {
    "token": fields.String(required=True, description="Plaid link token")
})

error_model = plaid_ns.model("Error", {
    "error": fields.String(required=True, description="Error message"),
    "message": fields.String(required=True, description="Error message")
})

public_token_model = plaid_ns.model("PublicToken", {
    "token": fields.String(required=True, description="Plaid public token")
})

# Create facade instance
plaid_facade = PlaidFacade()

@plaid_ns.route("/create-link-token")
class CreateLinkToken(Resource):
    @plaid_ns.doc("create_link_token")
    @plaid_ns.response(200, "Plaid link token created", link_token_model)
    @plaid_ns.response(400, "Validation error", error_model)
    @plaid_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        return plaid_facade.create_link_token(user_id)
    
@plaid_ns.route("/create-public-token")
class CreatePublicToken(Resource):
    @plaid_ns.doc("create_public_token")
    @plaid_ns.response(200, "Plaid public token created", public_token_model)
    @plaid_ns.response(400, "Validation error", error_model)
    @plaid_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        return plaid_facade.create_sandbox_public_token(user_id)
    
@plaid_ns.route("/exchange-public-token")
class ExchangePublicToken(Resource):
    @plaid_ns.doc("exchange_public_token")
    @plaid_ns.response(200, "Plaid public token exchanged", public_token_model)
    @plaid_ns.response(400, "Validation error", error_model)
    @plaid_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        data = request.get_json()
        public_token = data.get("public_token")
        if not public_token:
            raise ValueError("Missing public_token in request body")
        user_id = get_jwt_identity()
        return plaid_facade.exchange_public_token(user_id, public_token)
    
@plaid_ns.route("/disconnect")
class Disconnect(Resource):
    @plaid_ns.doc("disconnect")
    @plaid_ns.response(200, "Plaid disconnected")
    @plaid_ns.response(400, "Validation error", error_model)
    @plaid_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        return plaid_facade.disconnect(user_id)
