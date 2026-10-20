from datetime import datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Numeric, String, Time, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from entities.transaction import Transaction

 
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    monthly_income: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    usual_city: Mapped[str] = mapped_column(String(80))
    usual_start_time: Mapped[time] = mapped_column(Time)
    usual_end_time: Mapped[time] = mapped_column(Time)
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="client",
        passive_deletes="all",
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name!r}>"