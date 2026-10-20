from config.exceptions import ConflictError, NotFoundError
from entities.rule import Rule
from repositories.rule_repository import RuleRepository
from schemas.rule_schema import RuleCreate, RuleUpdate

class RuleService:
    def __init__(self, repository: RuleRepository) -> None:
        self._repository = repository

    def list_rules(self, skip: int = 0, limit: int = 100) -> list[Rule]:
        return self._repository.list_all(skip, limit)

    def get_rule(self, rule_id: int) -> Rule:
        rule = self._repository.get_by_id(rule_id)

        if rule is None:
            raise NotFoundError(f"Rule {rule_id} not found.")
        
        return rule

    def create_rule(self, data: RuleCreate) -> Rule:
        if self._repository.find_by_code(data.code) is not None:
            raise ConflictError(f"A rule with code '{data.code}' already exists.")
        
        return self._repository.add(Rule(**data.model_dump()))

    def update_rule(self, rule_id: int, data: RuleUpdate) -> Rule:
        rule = self.get_rule(rule_id)

        for field, value in data.model_dump().items():
            setattr(rule, field, value)

        return self._repository.update(rule)

    def delete_rule(self, rule_id: int) -> None:
        rule = self.get_rule(rule_id)

        if self._repository.has_alerts(rule.id):
            raise ConflictError(
                "This rule has already generated alerts and cannot be deleted. "
                "Deactivate it instead."
            )
        
        self._repository.delete(rule)