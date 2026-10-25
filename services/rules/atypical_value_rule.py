import statistics

from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.text_utils import describe_minutes, format_decimal


class AtypicalValueRule(AnomalyRule):
    code = "ATYPICAL_VALUE"
    uses_history = True

    MIN_SAMPLE = 5

    def evaluate(self, context: EvaluationContext) -> str | None:
        if self._threshold is None or self._window_minutes is None:
            return None

        amounts = [past.amount for past in self._history_in_window(context)]

        if len(amounts) < self.MIN_SAMPLE:
            return None

        average = statistics.mean(amounts)
        spread = statistics.stdev(amounts)

        if spread == 0:
            spread = average

        limit = average + self._threshold * spread
        amount = context.transaction.amount

        if amount <= limit:
            return None

        unit = "standard deviation" if self._threshold == 1 else "standard deviations"

        return (
            f"Amount {amount:.2f} is above the client's usual range "
            f"(average {average:.2f} + {format_decimal(self._threshold)} "
            f"{unit} = {limit:.2f}, based on {len(amounts)} "
            f"transactions in the last {describe_minutes(self._window_minutes)})"
        )