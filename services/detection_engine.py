from dataclasses import dataclass

from entities.rule import Rule
from entities.transaction import Classification
from services.rules.anomaly_rule import AnomalyRule, EvaluationContext
from services.rules.atypical_value_rule import AtypicalValueRule
from services.rules.consecutive_increasing_rule import ConsecutiveIncreasingRule
from services.rules.high_frequency_rule import HighFrequencyRule
from services.rules.profile_mismatch_rule import ProfileMismatchRule
from services.rules.repeated_similar_rule import RepeatedSimilarRule
from services.rules.unusual_hour_rule import UnusualHourRule
from services.rules.unusual_location_rule import UnusualLocationRule

@dataclass(frozen=True)
class Finding:
    rule_id: int
    reason: str
    points: int

@dataclass(frozen=True)
class Analysis:
    score: int
    classification: Classification
    findings: list[Finding]

class DetectionEngine:
    MAX_SCORE = 100
    ATTENTION_FROM = 30
    SUSPICIOUS_FROM = 60

    _RULE_CLASSES: tuple[type[AnomalyRule], ...] = (
        UnusualHourRule,
        UnusualLocationRule,
        ProfileMismatchRule,
        HighFrequencyRule,
        RepeatedSimilarRule,
        ConsecutiveIncreasingRule,
        AtypicalValueRule,
    )

    def __init__(self, definitions: list[Rule]) -> None:
        classes_by_code = {cls.code: cls for cls in self._RULE_CLASSES}

        self._rules: list[AnomalyRule] = [
            classes_by_code[definition.code](definition)
            for definition in definitions
            if definition.code in classes_by_code
        ]

    @property
    def history_window_minutes(self) -> int:
        return max(
            (rule.window_minutes or 0 for rule in self._rules if rule.uses_history),
            default=0,
        )

    def analyze(self, context: EvaluationContext) -> Analysis:
        findings = []

        for rule in self._rules:
            reason = rule.evaluate(context)
            if reason is not None:
                findings.append(Finding(rule.rule_id, reason, rule.weight))

        score = min(sum(finding.points for finding in findings), self.MAX_SCORE)

        return Analysis(score, self.classify(score), findings)

    @classmethod
    def classify(cls, score: int) -> Classification:
        if score >= cls.SUSPICIOUS_FROM:
            return Classification.SUSPICIOUS
        
        if score >= cls.ATTENTION_FROM:
            return Classification.ATTENTION
        
        return Classification.NORMAL