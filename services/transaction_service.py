from datetime import datetime, timedelta

from config.clock import now, to_naive_local
from config.exceptions import BusinessRuleError, NotFoundError
from entities.alert import Alert
from entities.client import Client
from entities.transaction import Classification, Transaction
from repositories.client_repository import ClientRepository
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from schemas.transaction_schema import TransactionCreate, TransactionUpdate
from services.detection_engine import DetectionEngine
from services.rules.anomaly_rule import EvaluationContext

class TransactionService:
    FUTURE_TOLERANCE = timedelta(minutes=1)

    def __init__(
        self,
        repository: TransactionRepository,
        client_repository: ClientRepository,
        rule_repository: RuleRepository,
    ) -> None:
        self._repository = repository
        self._client_repository = client_repository
        self._rule_repository = rule_repository

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

        self._analyze(transaction, client)

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

        # An edited transaction must be analysed again: the old alerts no
        # longer apply. They are deleted first, because the new analysis may
        # flag the same rule again (alerts are unique per transaction + rule).
        transaction.alerts.clear()
        self._repository.flush()

        client = self._client_repository.get_by_id(transaction.client_id)
        self._analyze(transaction, client)
        return self._repository.update(transaction)

    def delete_transaction(self, transaction_id: int) -> None:
        transaction = self.get_transaction(transaction_id)
        self._repository.delete(transaction)

    def _analyze(self, transaction: Transaction, client: Client) -> None:
        engine = DetectionEngine(self._rule_repository.list_active())

        history = []

        if engine.history_window_minutes > 0:
            since = transaction.occurred_at - timedelta(
                minutes=engine.history_window_minutes
            )
            history = self._repository.list_history(
                client.id, since, transaction.occurred_at, transaction.id
            )

        analysis = engine.analyze(EvaluationContext(transaction, client, history))

        transaction.risk_score = analysis.score
        transaction.classification = analysis.classification.value

        for finding in analysis.findings:
            transaction.alerts.append(
                Alert(
                    rule_id=finding.rule_id,
                    reason=finding.reason,
                    points=finding.points,
                )
            )

    def _validated_date(self, occurred_at: datetime) -> datetime:
        local_time = to_naive_local(occurred_at)

        if local_time > now() + self.FUTURE_TOLERANCE:
            raise BusinessRuleError(
                "The transaction date and time cannot be in the future."
            )
        
        return local_time