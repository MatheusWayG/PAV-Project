from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.database import get_db
from entities.client import Client
from repositories.client_repository import ClientRepository
from services.auth_service import AuthService
from services.password_hasher import PasswordHasher
from services.token_service import TokenService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    description="Log in with your CPF (in the 'username' field) and your password.",
)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(ClientRepository(db), PasswordHasher(), TokenService())

def get_current_client(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> Client:
    return auth_service.authenticate(token)
