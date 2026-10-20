from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    Numeric,
    String,
    Text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from entities.alert import Alert

class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint("weight BETWEEN 1 AND 100", name="ck_rules_weight_range"),
        CheckConstraint(
            "threshold IS NULL OR threshold >= 0",
            name="ck_rules_threshold_non_negative",
        ),
        CheckConstraint(
            "window_minutes IS NULL OR window_minutes > 0",
            name="ck_rules_window_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    weight: Mapped[int] = mapped_column(Integer)  # points added to the score
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    window_minutes: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true()
    )

    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="rule",
        passive_deletes="all",
    )

    def __repr__(self) -> str:
        return f"<Rule id={self.id} code={self.code!r}>"