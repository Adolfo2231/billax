from app.services.ai_config import AIService
from app.repositories.chat_repository import ChatRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
from app.config import Config
from typing import Dict, Any, List
import re
import pprint


class ChatFacade:
    def __init__(self):
        self.ai_service = AIService()
        self.chat_repository = ChatRepository()
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()
        self.transaction_repository = TransactionRepository()

    def get_financial_context(self, user_id: int, selected_account_id: str = None) -> Dict[str, Any]:
        """
        Obtiene el contexto financiero del usuario.
        Args:
            user_id (int): ID del usuario
            selected_account_id (str): ID de la cuenta seleccionada para filtrar transacciones
        Returns:
            Dict[str, Any]: Contexto financiero con cuentas y transacciones
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return {
                    "accounts": [],
                    "transactions": [],
                    "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "note": "Usuario no encontrado"
                }

            accounts = self.account_repository.get_by_user_id(user_id)
            accounts_data = [account.to_dict() for account in accounts]

            if selected_account_id:
                selected_account = next((acc for acc in accounts if str(acc.id) == str(selected_account_id)), None)
                if selected_account:
                    transactions = self.transaction_repository.get_by_account_id(selected_account.plaid_account_id)
                    transactions_data = [tx.to_dict() for tx in transactions]
                    accounts_data = [selected_account.to_dict()]
                else:
                    transactions_data = []
            else:
                transactions = self.transaction_repository.get_by_user_id(user_id)
                transactions_data = [tx.to_dict() for tx in transactions]

            for tx in transactions_data:
                if isinstance(tx.get('name'), str):
                    tx['name'] = re.sub(r'[*/: ]+$', '', tx['name'])

            transactions_data.sort(key=lambda t: t.get('date', ''), reverse=True)

            print("==== [DEBUG] get_financial_context ====")
            print(f"selected_account_id: {selected_account_id}")
            print(f"accounts_data: {accounts_data}")
            print(f"transactions_data: {transactions_data}")
            print("==== [DEBUG] END get_financial_context ====")

            return {
                "accounts": accounts_data,
                "transactions": transactions_data,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "selected_account_id": selected_account_id
            }

        except Exception as e:
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

    def message(self, user_id: int, message: str, selected_account_id: str = None) -> Dict[str, Any]:
        print(f"==== INICIO message() ====")
        print(f"User ID: {user_id}")
        print(f"Message: {message}")
        print(f"Selected Account ID: {selected_account_id}")

        print("Obteniendo contexto financiero...")
        financial_context = self.get_financial_context(user_id, selected_account_id)
        print(f"[DEBUG] Contexto financiero enviado a la IA: {financial_context}")
        print(f"Contexto obtenido con {len(financial_context.get('accounts', []))} cuentas y {len(financial_context.get('transactions', []))} transacciones")

        # Si solo hay una cuenta, modifica la pregunta para que sea explícita
        accounts = financial_context.get('accounts', [])
        if len(accounts) == 1:
            account_name = accounts[0].get('name', 'esta cuenta')
            user_message = f"Para la cuenta {account_name}, {message}"
            print(f"[DEBUG] Pregunta modificada para IA: {user_message}")
        else:
            user_message = message

        print("Obteniendo historial de chat...")
        chat_history = self.get_chat_history(user_id, format_type="ai")
        print(f"Historial obtenido: {len(chat_history)} mensajes")

        print("Enviando a AIService...")
        ai_response = self.ai_service.get_chat_response(user_message, financial_context, chat_history)
        print(f"Respuesta de AI recibida: {len(ai_response.get('response', ''))} caracteres")

        print("Guardando en base de datos...")
        self.chat_repository.save(user_id, message, ai_response["response"])
        print("Mensaje guardado exitosamente")

        print("==== FIN message() ====")

        return {
            "response": ai_response["response"]
        }
    
    def delete_chat_id(self, user_id: int, chat_id: int):
        self.chat_repository.delete_by_id(chat_id)
    
    def delete_all_chats(self, user_id: int):
        self.chat_repository.delete_all_by_user_id(user_id)

