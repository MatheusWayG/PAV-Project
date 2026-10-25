from datetime import time

from services.rules.anomaly_rule import AnomalyRule, EvaluationContext

MINUTES_PER_DAY = 24 * 60

class UnusualHourRule(AnomalyRule):
    code = "UNUSUAL_HOUR"

    def evaluate(self, context: EvaluationContext) -> str | None:
        client = context.client

        start = self._to_minutes(client.usual_start_time)
        end = self._to_minutes(client.usual_end_time)
        tolerance = int(self._threshold or 0)

        usual_span = (end - start) % MINUTES_PER_DAY

        if usual_span == 0:
            return None
        
        allowed_span = usual_span + 2 * tolerance

        if allowed_span >= MINUTES_PER_DAY:
            return None

        occurred_at = context.transaction.occurred_at

        moment = self._to_minutes(occurred_at.time())

        offset = (moment - (start - tolerance)) % MINUTES_PER_DAY

        if offset <= allowed_span:
            return None

        reason = (
            f"Transaction at {occurred_at:%H:%M} is outside the client's usual "
            f"hours ({client.usual_start_time:%H:%M}-{client.usual_end_time:%H:%M})"
        )
        if tolerance:
            reason += f" with a tolerance of {tolerance} min"

        return reason

    @staticmethod
    def _to_minutes(moment: time) -> int:
        return moment.hour * 60 + moment.minute