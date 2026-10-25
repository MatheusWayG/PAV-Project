from config.exceptions import BusinessRuleError, ConflictError, NotFoundError
from entities.alert import Alert
from entities.transaction import Classification
from repositories.alert_repository import AlertRepository
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from schemas.alert_schema import AlertCreate, AlertUpdate

class AlertService:
    def __init__(
        self,
        repository: AlertRepository,
        transaction_repository: TransactionRepository,
        rule_repository: RuleRepository,
    ) -> None:
        self._repository = repository
        self._transaction_repository = transaction_repository
        self._rule_repository = rule_repository

    def list_alerts(
        self,
        transaction_id: int | None = None,
        rule_id: int | None = None,
        classification: Classification | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Alert]:
        if (
            transaction_id is not None
            and self._transaction_repository.get_by_id(transaction_id) is None
        ):
            raise NotFoundError(f"Transaction {transaction_id} not found.")
        
        if rule_id is not None and self._rule_repository.get_by_id(rule_id) is None:
            raise NotFoundError(f"Rule {rule_id} not found.")
        
        label = classification.value if classification else None

        return self._repository.list_filtered(
            transaction_id, rule_id, label, skip, limit
        )

    def get_alert(self, alert_id: int) -> Alert:
        alert = self._repository.get_by_id(alert_id)

        if alert is None:
            raise NotFoundError(f"Alert {alert_id} not found.")
        
        return alert

    def create_alert(self, data: AlertCreate) -> Alert:
        if self._transaction_repository.get_by_id(data.transaction_id) is None:
            raise BusinessRuleError(
                f"Transaction {data.transaction_id} does not exist."
            )
        
        if self._rule_repository.get_by_id(data.rule_id) is None:
            raise BusinessRuleError(f"Rule {data.rule_id} does not exist.")
        
        existing = self._repository.find_by_transaction_and_rule(
            data.transaction_id, data.rule_id
        )

        if existing is not None:
            raise ConflictError("This rule has already flagged this transaction.")
        
        return self._repository.add(Alert(**data.model_dump()))

    def update_alert(self, alert_id: int, data: AlertUpdate) -> Alert:
        alert = self.get_alert(alert_id)
        alert.reason = data.reason
        return self._repository.update(alert)

    def delete_alert(self, alert_id: int) -> None:
        alert = self.get_alert(alert_id)
        self._repository.delete(alert)