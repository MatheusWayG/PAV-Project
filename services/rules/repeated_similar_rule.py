from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.text_utils import (
    describe_minutes,
    format_decimal,
    normalize_text,
)

class RepeatedSimilarRule(AnomalyRule):
    code = "REPEATED_SIMILAR"
    uses_history = True

    def evaluate(self, context: EvaluationContext) -> str | None:
        if self._threshold is None or self._window_minutes is None:
            return None

        current = context.transaction
        destination = normalize_text(current.destination)

        similar = [
            past
            for past in self._history_in_window(context)
            if past.amount == current.amount
            and normalize_text(past.destination) == destination
        ]

        count = len(similar) + 1

        if count < self._threshold:
            return None

        return (
            f"{count} transactions of {current.amount:.2f} to "
            f"'{current.destination}' within "
            f"{describe_minutes(self._window_minutes)} "
            f"(limit: {format_decimal(self._threshold)})"
        )