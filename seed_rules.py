from decimal import Decimal

import entities
from config.database import SessionLocal
from repositories.rule_repository import RuleRepository
from schemas.rule_schema import RuleCreate
from services.rule_service import RuleService

DEFAULT_RULES = [
    RuleCreate(
        code="ATYPICAL_VALUE",
        name="Atypical amount",
        description=(
            "Amount above the client's average over the last window_minutes "
            "plus threshold standard deviations (window: 30 days)."
        ),
        weight=30,
        threshold=Decimal("3"),
        window_minutes=43200,
    ),
    RuleCreate(
        code="HIGH_FREQUENCY",
        name="High frequency",
        description=(
            "At least threshold transactions by the same client within "
            "window_minutes."
        ),
        weight=25,
        threshold=Decimal("5"),
        window_minutes=10,
    ),
    RuleCreate(
        code="UNUSUAL_HOUR",
        name="Unusual hour",
        description=(
            "Transaction outside the client's usual hours, with a tolerance "
            "of threshold minutes (0 = strict)."
        ),
        weight=15,
        threshold=Decimal("0"),
    ),
    RuleCreate(
        code="REPEATED_SIMILAR",
        name="Repeated similar transactions",
        description=(
            "At least threshold transactions with the same amount and "
            "destination within window_minutes."
        ),
        weight=25,
        threshold=Decimal("3"),
        window_minutes=60,
    ),
    RuleCreate(
        code="CONSECUTIVE_INCREASING",
        name="Consecutive increasing amounts",
        description=(
            "Sequence of threshold transactions, each larger than the "
            "previous one, within window_minutes."
        ),
        weight=20,
        threshold=Decimal("3"),
        window_minutes=60,
    ),
    RuleCreate(
        code="PROFILE_MISMATCH",
        name="Incompatible with client profile",
        description=(
            "Amount greater than threshold times the client's declared "
            "monthly income (0.50 = 50%)."
        ),
        weight=20,
        threshold=Decimal("0.50"),
    ),
    RuleCreate(
        code="UNUSUAL_LOCATION",
        name="Unusual location",
        description="Transaction location differs from the client's usual city.",
        weight=20,
    ),
]

def main() -> None:
    db = SessionLocal()

    try:
        repository = RuleRepository(db)
        service = RuleService(repository)
        created = skipped = 0

        for rule in DEFAULT_RULES:
            if repository.find_by_code(rule.code) is not None:
                skipped += 1
            else:
                service.create_rule(rule)
                created += 1
                
        print(f"Rules created: {created} | already existed: {skipped}")
    finally:
        db.close()

if __name__ == "__main__":
    main()