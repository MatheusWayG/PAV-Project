from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from entities.alert import Alert
    from entities.client import Client

class TransactionType(str, Enum):
    PIX = "PIX"
    TED = "TED"
    CARD = "CARD"
    WITHDRAWAL = "WITHDRAWAL"
    BOLETO = "BOLETO"

class Classification(str, Enum):
    NORMAL = "NORMAL"
    ATTENTION = "ATTENTION"
    SUSPICIOUS = "SUSPICIOUS"

_CLASSIFICATION_VALUES = ", ".join(f"'{c.value}'" for c in Classification)

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "risk_score BETWEEN 0 AND 100",
            name="ck_transactions_risk_score_range",
        ),
        CheckConstraint(
            f"classification IN ({_CLASSIFICATION_VALUES})",
            name="ck_transactions_classification",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    transaction_type: Mapped[str] = mapped_column(String(30))
    destination: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(80))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    risk_score: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    classification: Mapped[str] = mapped_column(
        String(20),
        default=Classification.NORMAL.value,
        server_default=Classification.NORMAL.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    client: Mapped["Client"] = relationship(back_populates="transactions")

    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Alert.id",
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction id={self.id} amount={self.amount} "
            f"classification={self.classification}>"
        )