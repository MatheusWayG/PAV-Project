from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from entities.alert import Alert
from entities.transaction import Transaction
from repositories.base_repository import BaseRepository

class AlertRepository(BaseRepository[Alert]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Alert)

    def list_filtered(
        self,
        transaction_id: int | None = None,
        rule_id: int | None = None,
        classification: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Alert]:
        statement = select(Alert).options(joinedload(Alert.rule))

        if transaction_id is not None:
            statement = statement.where(Alert.transaction_id == transaction_id)

        if rule_id is not None:
            statement = statement.where(Alert.rule_id == rule_id)

        if classification is not None:
            statement = statement.join(
                Transaction, Alert.transaction_id == Transaction.id
            ).where(Transaction.classification == classification)

        statement = statement.order_by(Alert.id.desc()).offset(skip).limit(limit)

        return list(self._db.scalars(statement))

    def find_by_transaction_and_rule(
        self, transaction_id: int, rule_id: int
    ) -> Alert | None:
        statement = select(Alert).where(
            Alert.transaction_id == transaction_id, Alert.rule_id == rule_id
        )

        return self._db.scalars(statement).first()