from app.services.ai_config import AIService
from app.repositories.chat_repository import ChatRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
from app.config import Config
from typing import Dict, Any, List


class ChatFacade:
    def __init__(self):
        self.ai_service = AIService()
        self.chat_repository = ChatRepository()
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()
        self.transaction_repository = TransactionRepository()

    def get_financial_context(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el contexto financiero del usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            Dict[str, Any]: Contexto financiero con cuentas y transacciones
        """
        try:
            # Obtener el usuario
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return {
                    "accounts": [],
                    "transactions": [],
                    "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "note": "Usuario no encontrado"
                }
            
            # Obtener cuentas y transacciones de la base de datos local
            accounts = self.account_repository.get_by_user_id(user_id)
            transactions = self.transaction_repository.get_by_user_id(user_id)
            
            # Usar to_dict() para serializar
            accounts_data = [account.to_dict() for account in accounts]
            transactions_data = [transaction.to_dict() for transaction in transactions]
            
            return {
                "accounts": accounts_data,
                "transactions": transactions_data,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            # En caso de error, retornar contexto sin datos financieros
            return {
                "accounts": [],
                "transactions": [],
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "note": f"Error obteniendo datos financieros: {str(e)}"
            }

    def get_chat_history(self, user_id: int, format_type: str = "complete") -> List[Dict[str, Any]]:
        """
        Obtiene el historial de chat del usuario.
        
        Args:
            user_id (int): ID del usuario
            format_type (str): Tipo de formato ("complete" para UI, "ai" para OpenAI)
            
        Returns:
            List[Dict[str, Any]]: Historial de chat en el formato especificado
        """
        try:
            chat_history = self.chat_repository.get_user_history(user_id)
            formatted_history = []
            
            for chat in chat_history:
                if format_type == "ai":
                    # Formato para OpenAI
                    formatted_history.append({"role": "user", "content": chat.message})
                    formatted_history.append({"role": "assistant", "content": chat.response})
                else:
                    # Formato completo para UI
                    formatted_history.append({
                        "id": chat.id,
                        "message": chat.message,
                        "response": chat.response,
                        "created_at": chat.created_at.isoformat() if chat.created_at else None
                    })
            
            return formatted_history
            
        except Exception as e:
            return []

    def message(self, user_id: int, message: str) -> Dict[str, Any]:
        """
        Send a message to the AI and save the conversation to the database.

        Args:
            user_id (int): The ID of the user sending the message.
            message (str): The message to send to the AI.
            
        Returns:
            Dict[str, Any]: The AI response only
        """
        
        # Get the user's financial context
        financial_context = self.get_financial_context(user_id)
        
        # Get chat history for AI
        chat_history = self.get_chat_history(user_id, format_type="ai")
        
        # Get the AI response
        ai_response = self.ai_service.get_chat_response(message, financial_context, chat_history)

        # Save the message and response to the database
        self.chat_repository.save(user_id, message, ai_response["response"])
        
        # Return only the AI response, not the full context
        return {
            "response": ai_response["response"]
        }
    
    def delete_chat_id(self, user_id: int, chat_id: int):
        self.chat_repository.delete_by_id(chat_id)
    
    def delete_all_chats(self, user_id: int):
        self.chat_repository.delete_all_by_user_id(user_id)

