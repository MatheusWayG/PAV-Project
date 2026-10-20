from datetime import datetime, timedelta

from config.clock import now, to_naive_local
from config.exceptions import BusinessRuleError, NotFoundError
from entities.transaction import Classification, Transaction
from repositories.client_repository import ClientRepository
from repositories.transaction_repository import TransactionRepository
from schemas.transaction_schema import TransactionCreate, TransactionUpdate


class TransactionService:
    # Small margin for clock differences between the client and the server.
    FUTURE_TOLERANCE = timedelta(minutes=1)

    def __init__(
        self,
        repository: TransactionRepository,
        client_repository: ClientRepository,
    ) -> None:
        self._repository = repository
        self._client_repository = client_repository

    def list_transactions(
        self,
        client_id: int | None = None,
        classification: Classification | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        if client_id is not None and self._client_repository.get_by_id(client_id) is None:
            raise NotFoundError(f"Client {client_id} not found.")
        
        label = classification.value if classification else None

        return self._repository.list_filtered(client_id, label, skip, limit)

    def get_transaction(self, transaction_id: int) -> Transaction:
        transaction = self._repository.get_by_id(transaction_id)

        if transaction is None:
            raise NotFoundError(f"Transaction {transaction_id} not found.")
        
        return transaction

    def create_transaction(self, data: TransactionCreate) -> Transaction:
        client = self._client_repository.get_by_id(data.client_id)

        if client is None:
            raise BusinessRuleError(f"Client {data.client_id} does not exist.")
        
        if not client.active:
            raise BusinessRuleError(
                "This client is inactive and cannot receive new transactions."
            )

        values = data.model_dump()
        values["transaction_type"] = data.transaction_type.value
        values["occurred_at"] = self._validated_date(data.occurred_at)

        transaction = Transaction(**values)

        #TODO: the detection engine will evaluate the new transaction here.
        return self._repository.add(transaction)

    def update_transaction(
        self, transaction_id: int, data: TransactionUpdate
    ) -> Transaction:
        transaction = self.get_transaction(transaction_id)

        transaction.amount = data.amount
        transaction.transaction_type = data.transaction_type.value
        transaction.destination = data.destination
        transaction.location = data.location
        transaction.occurred_at = self._validated_date(data.occurred_at)

        self._reevaluate(transaction)

        return self._repository.update(transaction)

    def delete_transaction(self, transaction_id: int) -> None:
        transaction = self.get_transaction(transaction_id)
        self._repository.delete(transaction)

    def _validated_date(self, occurred_at: datetime) -> datetime:
        local_time = to_naive_local(occurred_at)

        if local_time > now() + self.FUTURE_TOLERANCE:
            raise BusinessRuleError(
                "The transaction date and time cannot be in the future."
            )
        
        return local_time

    @staticmethod
    def _reevaluate(transaction: Transaction) -> None:
        """An edited transaction must be analysed again.

        The old analysis no longer applies, so its alerts and score are
        discarded. Next step: the detection engine will be called here to
        produce the new score and alerts.
        """
        transaction.alerts.clear()
        transaction.risk_score = 0
        transaction.classification = Classification.NORMAL.value