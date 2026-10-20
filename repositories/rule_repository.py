from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from entities.alert import Alert
from entities.rule import Rule
from repositories.base_repository import BaseRepository

class RuleRepository(BaseRepository[Rule]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Rule)

    def find_by_code(self, code: str) -> Rule | None:
        statement = select(Rule).where(Rule.code == code)
        return self._db.scalars(statement).first()

    def list_active(self) -> list[Rule]:
        statement = select(Rule).where(Rule.active.is_(True)).order_by(Rule.id)
        return list(self._db.scalars(statement))

    def has_alerts(self, rule_id: int) -> bool:
        statement = select(exists().where(Alert.rule_id == rule_id))
        return bool(self._db.scalar(statement))