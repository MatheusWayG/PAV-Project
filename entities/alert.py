from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from entities.rule import Rule
    from entities.transaction import Transaction

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        UniqueConstraint(
            "transaction_id", "rule_id", name="uq_alerts_transaction_rule"
        ),
        CheckConstraint("points > 0", name="ck_alerts_points_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), index=True
    )
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("rules.id", ondelete="RESTRICT"), index=True
    )
    reason: Mapped[str] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    transaction: Mapped["Transaction"] = relationship(back_populates="alerts")
    rule: Mapped["Rule"] = relationship(back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} rule_id={self.rule_id} points={self.points}>"