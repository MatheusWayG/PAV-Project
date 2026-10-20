from schemas.rule_schema import RuleCreate, RuleOut, RuleUpdate
from services.rule_service import RuleService

class RuleController:
    def __init__(self, service: RuleService) -> None:
        self._service = service

    def list_rules(self, skip: int, limit: int) -> list[RuleOut]:
        rules = self._service.list_rules(skip, limit)
        return [RuleOut.model_validate(rule) for rule in rules]

    def get_rule(self, rule_id: int) -> RuleOut:
        return RuleOut.model_validate(self._service.get_rule(rule_id))

    def create_rule(self, data: RuleCreate) -> RuleOut:
        return RuleOut.model_validate(self._service.create_rule(data))

    def update_rule(self, rule_id: int, data: RuleUpdate) -> RuleOut:
        return RuleOut.model_validate(self._service.update_rule(rule_id, data))

    def delete_rule(self, rule_id: int) -> None:
        self._service.delete_rule(rule_id)