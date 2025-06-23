from app.repositories.user_repository import UserRepository
from app.services.plaid_config import create_link_plaid
from app.services.plaid_config import plaid_public_token
from app.utils.plaid_exceptions import PlaidUserAlreadyLinkedError, PlaidUserNotFoundError

class PlaidFacade:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_link_token(self, user_id):
        # 1. Verificar que el usuario existe en la BD
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        
        if user.plaid_access_token:
            raise PlaidUserAlreadyLinkedError()
        
        return create_link_plaid(user_id)
    
    def create_public_token(self, user_id):
        # 1. Verificar que el usuario existe en la BD
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        
        # 2. Verificar que NO tenga access token (porque si lo tiene, no necesita public token)
        if user.plaid_access_token:
            raise PlaidUserAlreadyLinkedError("User already has Plaid connected")
        
        # 3. Crear public token
        return plaid_public_token()