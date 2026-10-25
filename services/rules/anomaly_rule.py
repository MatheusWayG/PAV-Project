from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta

from entities.client import Client
from entities.rule import Rule
from entities.transaction import Transaction

@dataclass(frozen=True)
class EvaluationContext:
    transaction: Transaction
    client: Client
    history: list[Transaction] = field(default_factory=list)

class AnomalyRule(ABC):
    code: str
    uses_history: bool = False

    def __init__(self, definition: Rule) -> None:
        self._rule_id = definition.id
        self._weight = definition.weight
        self._threshold = definition.threshold
        self._window_minutes = definition.window_minutes

    @property
    def rule_id(self) -> int:
        return self._rule_id

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def window_minutes(self) -> int | None:
        return self._window_minutes

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> str | None:
        """Returns the reason if the transaction is anomalous, else None."""

    def _history_in_window(self, context: EvaluationContext) -> list[Transaction]:
        if self._window_minutes is None:
            return []
        
        end = context.transaction.occurred_at
        start = end - timedelta(minutes=self._window_minutes)

        return [t for t in context.history if start <= t.occurred_at <= end]