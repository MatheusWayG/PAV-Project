from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from entities.client import Client
from entities.transaction import Transaction
from repositories.base_repository import BaseRepository

class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Client)

    def find_by_cpf(self, cpf: str) -> Client | None:
        statement = select(Client).where(Client.cpf == cpf)
        return self._db.scalars(statement).first()

    def has_transactions(self, client_id: int) -> bool:
        statement = select(exists().where(Transaction.client_id == client_id))
        return bool(self._db.scalar(statement))