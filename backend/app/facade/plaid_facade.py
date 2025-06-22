from app.repositories.user_repository import UserRepository
from app.services.plaid_config import create_link_plaid
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