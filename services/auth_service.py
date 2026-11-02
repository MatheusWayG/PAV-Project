from config.exceptions import UnauthorizedError
from entities.client import Client
from repositories.client_repository import ClientRepository
from schemas.auth_schema import TokenOut
from services.cpf_validator import CpfValidator
from services.password_hasher import PasswordHasher
from services.token_service import TokenService

MAX_PASSWORD_LENGTH = 128

_DUMMY_HASH = PasswordHasher().hash("not-a-real-password")


class AuthService:
    _LOGIN_ERROR = "Invalid CPF or password."

    def __init__(
        self,
        repository: ClientRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    def login(self, raw_cpf: str, password: str) -> TokenOut:
        client = self._find_client(raw_cpf)
        stored_hash = client.password_hash if client else _DUMMY_HASH

        password_ok = (
            len(password) <= MAX_PASSWORD_LENGTH
            and self._password_hasher.verify(password, stored_hash)
        )

        if client is None or not password_ok:
            raise UnauthorizedError(self._LOGIN_ERROR)

        if not client.active:
            raise UnauthorizedError("Client account is inactive.")

        return TokenOut(
            access_token=self._token_service.create_access_token(client.id),
            expires_in=self._token_service.expires_in_seconds,
        )

    def authenticate(self, token: str) -> Client:
        client_id = self._token_service.read_client_id(token)
        client = self._repository.get_by_id(client_id)

        if client is None:  # the account was deleted after the token was issued
            raise UnauthorizedError("Invalid token.")

        if not client.active:
            raise UnauthorizedError("Client account is inactive.")

        return client

    def get_me(self, current_client: Client) -> Client:
        return current_client

    def _find_client(self, raw_cpf: str) -> Client | None:
        if not CpfValidator.is_valid(raw_cpf):
            return None
        
        return self._repository.find_by_cpf(CpfValidator.normalize(raw_cpf))
