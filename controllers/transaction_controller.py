from entities.transaction import Classification
from schemas.transaction_schema import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)
from services.transaction_service import TransactionService

class TransactionController:
    def __init__(self, service: TransactionService) -> None:
        self._service = service

    def list_transactions(
        self,
        client_id: int | None,
        classification: Classification | None,
        skip: int,
        limit: int,
    ) -> list[TransactionOut]:
        transactions = self._service.list_transactions(
            client_id, classification, skip, limit
        )
        return [TransactionOut.model_validate(t) for t in transactions]

    def get_transaction(self, transaction_id: int) -> TransactionOut:
        transaction = self._service.get_transaction(transaction_id)
        return TransactionOut.model_validate(transaction)

    def create_transaction(self, data: TransactionCreate) -> TransactionOut:
        transaction = self._service.create_transaction(data)
        return TransactionOut.model_validate(transaction)

    def update_transaction(
        self, transaction_id: int, data: TransactionUpdate
    ) -> TransactionOut:
        transaction = self._service.update_transaction(transaction_id, data)
        return TransactionOut.model_validate(transaction)

    def delete_transaction(self, transaction_id: int) -> None:
        self._service.delete_transaction(transaction_id)