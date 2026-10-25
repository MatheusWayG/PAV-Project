from services.rules.anomaly_rule import AnomalyRule, EvaluationContext

class ProfileMismatchRule(AnomalyRule):
    code = "PROFILE_MISMATCH"

    def evaluate(self, context: EvaluationContext) -> str | None:
        if self._threshold is None:
            return None

        income = context.client.monthly_income
        amount = context.transaction.amount

        if amount <= income * self._threshold:
            return None

        percent = (self._threshold * 100).normalize()

        return (
            f"Amount {amount:.2f} exceeds {percent:f}% of the client's "
            f"monthly income ({income:.2f})"
        )