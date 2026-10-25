from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.text_utils import normalize_text

class UnusualLocationRule(AnomalyRule):
    code = "UNUSUAL_LOCATION"

    def evaluate(self, context: EvaluationContext) -> str | None:
        location = context.transaction.location
        usual_city = context.client.usual_city

        if normalize_text(location) == normalize_text(usual_city):
            return None
        
        return (
            f"Transaction location '{location}' differs from the client's "
            f"usual city '{usual_city}'"
        )