from flask_restx import Namespace, Resource, fields
from app.facade.plaid_facade import PlaidFacade
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity

plaid_ns = Namespace("plaid", description="Plaid API endpoints")

link_token_model = plaid_ns.model("LinkToken", {
    "token": fields.String(required=True, description="Plaid link token")
})

error_model = plaid_ns.model("Error", {
    "error": fields.String(required=True, description="Error message"),
    "message": fields.String(required=True, description="Error message")
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