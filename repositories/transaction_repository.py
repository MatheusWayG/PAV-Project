from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.transaction import Transaction
from repositories.base_repository import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Transaction)

    def list_filtered(
        self,
        client_id: int | None = None,
        classification: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        statement = select(Transaction)

        if client_id is not None:
            statement = statement.where(Transaction.client_id == client_id)

        if classification is not None:
            statement = statement.where(Transaction.classification == classification)

        statement = (
            statement.order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(self._db.scalars(statement))