from schemas.client_schema import ClientCreate, ClientOut, ClientUpdate
from services.client_service import ClientService

class ClientController:
    def __init__(self, service: ClientService) -> None:
        self._service = service

    def list_clients(self, skip: int, limit: int) -> list[ClientOut]:
        clients = self._service.list_clients(skip, limit)
        return [ClientOut.model_validate(client) for client in clients]

    def get_client(self, client_id: int) -> ClientOut:
        return ClientOut.model_validate(self._service.get_client(client_id))

    def create_client(self, data: ClientCreate) -> ClientOut:
        return ClientOut.model_validate(self._service.create_client(data))

    def update_client(self, client_id: int, data: ClientUpdate) -> ClientOut:
        client = self._service.update_client(client_id, data)
        return ClientOut.model_validate(client)

    def delete_client(self, client_id: int) -> None:
        self._service.delete_client(client_id)