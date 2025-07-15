from app.repositories.user_repository import UserRepository
from app.services.plaid_config import create_link_plaid, plaid_public_token, exchange_public_token
from app.utils.plaid_exceptions import PlaidUserAlreadyLinkedError, PlaidUserNotFoundError

class PlaidFacade:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_link_token(self, user_id):
        """Create a Plaid link token if user exists and hasn't linked Plaid yet."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        if user.plaid_access_token:
            raise PlaidUserAlreadyLinkedError()
        result = create_link_plaid(user_id)
        return {"link_token": result["link_token"]}

    def create_sandbox_public_token(self, user_id):
        """(Sandbox only) Create a public token for testing."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        if user.plaid_access_token:
            raise PlaidUserAlreadyLinkedError("User already has Plaid connected")
        return plaid_public_token()

    def exchange_public_token(self, user_id: int, public_token: str) -> str:
        """Exchange a public token for a real access token and save it to the user."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        access_token = exchange_public_token(public_token)
        user.plaid_access_token = access_token
        self.user_repository.update(user)
        return {"access_token": access_token}
    
    def disconnect(self, user_id: int) -> None:
        """Disconnect Plaid from the user and delete all accounts."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PlaidUserNotFoundError()
        user.plaid_access_token = None
        self.user_repository.update(user)
        # Delete all accounts for this user
        from app.repositories.account_repository import AccountRepository
        AccountRepository().delete_by_user_id(user_id)
        return {"message": "Plaid disconnected and accounts deleted"}

    def has_access_token(self, user_id: int) -> bool:
        """Return True if the user has a Plaid access token, False otherwise."""
        user = self.user_repository.get_by_id(user_id)
        return bool(user and user.plaid_access_token)
