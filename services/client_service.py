from entities.client import Client
from config.exceptions import BusinessRuleError, ConflictError, NotFoundError
from repositories.client_repository import ClientRepository
from schemas.client_schema import ClientCreate, ClientUpdate
from services.cpf_validator import CpfValidator

class ClientService:
    def __init__(self, repository: ClientRepository) -> None:
        self._repository = repository

    def list_clients(self, skip: int = 0, limit: int = 100) -> list[Client]:
        return self._repository.list_all(skip, limit)

    def get_client(self, client_id: int) -> Client:
        client = self._repository.get_by_id(client_id)

        if client is None:
            raise NotFoundError(f"Client {client_id} not found.")
        
        return client

    def create_client(self, data: ClientCreate) -> Client:
        cpf = self._validated_cpf(data.cpf)

        if self._repository.find_by_cpf(cpf) is not None:
            raise ConflictError("A client with this CPF is already registered.")

        values = data.model_dump()
        values["cpf"] = cpf

        return self._repository.add(Client(**values))

    def update_client(self, client_id: int, data: ClientUpdate) -> Client:
        client = self.get_client(client_id)
        cpf = self._validated_cpf(data.cpf)
        owner = self._repository.find_by_cpf(cpf)

        if owner is not None and owner.id != client.id:
            raise ConflictError("Another client already uses this CPF.")

        values = data.model_dump()
        values["cpf"] = cpf

        for field, value in values.items():
            setattr(client, field, value)

        return self._repository.update(client)

    def delete_client(self, client_id: int) -> None:
        client = self.get_client(client_id)

        if self._repository.has_transactions(client.id):
            raise ConflictError(
                "This client has transactions and cannot be deleted. "
                "Deactivate the client instead."
            )
        
        self._repository.delete(client)

    @staticmethod
    def _validated_cpf(raw_cpf: str) -> str:
        if not CpfValidator.is_valid(raw_cpf):
            raise BusinessRuleError("Invalid CPF.")
        
        return CpfValidator.normalize(raw_cpf)