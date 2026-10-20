from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.database import Base

ModelT = TypeVar("ModelT", bound=Base)

class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self._db = db
        self._model = model

    def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        statement = (
            select(self._model)
            .order_by(self._model.id)
            .offset(skip)
            .limit(limit)
        )

        return list(self._db.scalars(statement))

    def get_by_id(self, entity_id: int) -> ModelT | None:
        return self._db.get(self._model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self._db.add(entity)
        self._commit()
        self._db.refresh(entity)

        return entity

    def update(self, entity: ModelT) -> ModelT:
        self._commit()
        self._db.refresh(entity)
        
        return entity

    def delete(self, entity: ModelT) -> None:
        self._db.delete(entity)
        self._commit()

    def _commit(self) -> None:
        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise