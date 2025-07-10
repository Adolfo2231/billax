from app.extensions import db
from app.models.chat import Chat

class ChatRepository:
    def __init__(self):
        self.chat_model = Chat

    def save(self, user_id: int, message: str, response: str):
        print(f"[DEBUG] ChatRepository.save called with user_id={user_id}, message={message}, response={response}")
        chat = self.chat_model(user_id=user_id, message=message, response=response)
        print(f"[DEBUG] Chat instance created: {chat}")
        db.session.add(chat)
        db.session.commit()
        return chat
    
    def get_user_history(self, user_id: int, limit: int = 50):
        """
        Obtiene el historial de chat de un usuario.
        
        Args:
            user_id (int): ID del usuario
            limit (int): Número máximo de mensajes a retornar
            
        Returns:
            List[Chat]: Lista de mensajes de chat ordenados por fecha de creación (más antiguo primero)
        """
        return self.chat_model.query.filter_by(user_id=user_id)\
            .order_by(self.chat_model.created_at.asc())\
            .limit(limit)\
            .all()
    
    def delete_by_id(self, chat_id: int):
        self.chat_model.query.filter_by(id=chat_id).delete()
        db.session.commit()
    
    def delete_all_by_user_id(self, user_id: int):
        self.chat_model.query.filter_by(user_id=user_id).delete()
        db.session.commit()