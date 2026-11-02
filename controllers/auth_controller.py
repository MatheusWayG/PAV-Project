from entities.client import Client
from schemas.auth_schema import TokenOut
from schemas.client_schema import ClientOut
from services.auth_service import AuthService


class AuthController:
    def __init__(self, service: AuthService) -> None:
        self._service = service

    def login(self, cpf: str, password: str) -> TokenOut:
        return self._service.login(cpf, password)

    def get_me(self, current_client: Client) -> ClientOut:
        return ClientOut.model_validate(self._service.get_me(current_client))
