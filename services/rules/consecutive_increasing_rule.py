from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.text_utils import describe_minutes

class ConsecutiveIncreasingRule(AnomalyRule):
    code = "CONSECUTIVE_INCREASING"
    uses_history = True

    def evaluate(self, context: EvaluationContext) -> str | None:
        if self._threshold is None or self._window_minutes is None:
            return None

        past = sorted(
            self._history_in_window(context),
            key=lambda t: (t.occurred_at, t.id or 0),
        )

        run = [context.transaction.amount]

        for earlier in reversed(past):
            if earlier.amount < run[0]:
                run.insert(0, earlier.amount)
            else:
                break

        if len(run) < self._threshold:
            return None

        amounts = " -> ".join(f"{amount:.2f}" for amount in run)

        return (
            f"{len(run)} consecutive transactions with increasing amounts "
            f"({amounts}) within {describe_minutes(self._window_minutes)}"
        )