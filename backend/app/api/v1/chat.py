from flask_restx import Namespace, fields, Resource
from app.facade.chat_facade import ChatFacade
from app.utils.decorators.error_handler import handle_errors
from flask_jwt_extended import jwt_required, get_jwt_identity

chat_facade = ChatFacade()

chat_ns = Namespace("chat", description="Chat with the AI")

chat_model = chat_ns.model("Chat", {
    "message": fields.String(required=True, description="The message to send to the AI"),
})

chat_response_model = chat_ns.model("ChatResponse", {
    "response": fields.String(required=True, description="The response from the AI"),
})

chat_history_item_model = chat_ns.model("ChatHistoryItem", {
    "id": fields.Integer(description="Chat ID"),
    "message": fields.String(description="User message"),
    "response": fields.String(description="AI response"),
    "created_at": fields.String(description="Creation timestamp"),
})

chat_history_model = chat_ns.model("ChatHistory", {
    "history": fields.List(fields.Nested(chat_history_item_model), description="List of chat messages"),
})

error_model = chat_ns.model("Error", {
    "message": fields.String(required=True, description="The error message"),
})

@chat_ns.route("/")
class Chat(Resource):
    @chat_ns.doc("chat")
    @chat_ns.expect(chat_model)
    @chat_ns.response(200, "Chat successful", chat_response_model)
    @chat_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        message = chat_ns.payload.get("message")
        response = chat_facade.message(user_id, message)
        return response

@chat_ns.route("/history")
class ChatHistory(Resource):
    @chat_ns.doc("get_chat_history")
    @chat_ns.response(200, "Chat history retrieved successfully", chat_history_model)
    @chat_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        history = chat_facade.get_chat_history(user_id)
        return {"history": history}
    
@chat_ns.route("/delete/<int:chat_id>")
class DeleteChat(Resource):
    @chat_ns.doc("delete_chat")
    @chat_ns.response(200, "Chat deleted successfully")
    @chat_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def delete(self, chat_id):
        user_id = get_jwt_identity()
        chat_facade.delete_chat_id(user_id, chat_id)
        return {"message": "Chat deleted successfully"}, 200

@chat_ns.route("/delete/all")
class DeleteAllChats(Resource):
    @chat_ns.doc("delete_all_chats")
    @chat_ns.response(200, "All chats deleted successfully")
    @chat_ns.response(500, "Internal server error", error_model)
    @handle_errors
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        chat_facade.delete_all_chats(user_id)
        return {"message": "All chats deleted successfully"}, 200

