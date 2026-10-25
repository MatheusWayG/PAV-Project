from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.text_utils import describe_minutes, format_decimal

class HighFrequencyRule(AnomalyRule):
    code = "HIGH_FREQUENCY"
    uses_history = True

    def evaluate(self, context: EvaluationContext) -> str | None:
        if self._threshold is None or self._window_minutes is None:
            return None

        count = len(self._history_in_window(context)) + 1
        
        if count < self._threshold:
            return None

        return (
            f"{count} transactions within "
            f"{describe_minutes(self._window_minutes)} "
            f"(limit: {format_decimal(self._threshold)})"
        )