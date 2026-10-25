import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

import entities
from config.database import Base
from seed_rules import DEFAULT_RULES

INIT_SQL = Path(__file__).with_name("init.sql")
TIMEZONE = "America/Sao_Paulo"

def _ddl(element) -> str:
    return str(element.compile(dialect=postgresql.dialect())).strip() + ";"

def _literal(value) -> str:
    if value is None:
        return "NULL"
    
    if isinstance(value, (int, Decimal)):
        return str(value)
    
    return "'" + str(value).replace("'", "''") + "'"

def build_sql() -> str:
    parts = [
        "-- GENERATED FILE. Do not edit by hand.",
        "-- Regenerate with: python generate_init_sql.py",
        "-- Runs only the first time the database container starts (empty volume).",
        "",
        "-- Timestamps are stored in local time (same as the API).",
        "DO $$",
        "BEGIN",
        f"    EXECUTE format('ALTER DATABASE %I SET timezone TO %L', current_database(), '{TIMEZONE}');",
        "END",
        "$$;",
        "",
        "-- Tables",
    ]

    for table in Base.metadata.sorted_tables:
        parts += [_ddl(CreateTable(table, if_not_exists=True)), ""]

    parts.append("-- Indexes")

    indexes = sorted(
        (index for table in Base.metadata.sorted_tables for index in table.indexes),
        key=lambda index: index.name,
    )

    for index in indexes:
        parts.append(_ddl(CreateIndex(index, if_not_exists=True)))

    rows = ",\n".join(
        "    ("
        + ", ".join(
            _literal(value)
            for value in (
                rule.code,
                rule.name,
                rule.description,
                rule.weight,
                rule.threshold,
                rule.window_minutes,
            )
        )
        + ")"
        for rule in DEFAULT_RULES
    )

    parts += [
        "",
        "-- Default anomaly rules (the same ones as seed_rules.py)",
        "INSERT INTO rules (code, name, description, weight, threshold, window_minutes) VALUES",
        rows,
        "ON CONFLICT (code) DO NOTHING;",
        "",
    ]

    return "\n".join(parts)

def main() -> int:
    expected = build_sql()

    if "--check" in sys.argv:
        current = INIT_SQL.read_text(encoding="utf-8").replace("\r\n", "\n")

        if current == expected:
            print("init.sql is up to date.")
            return 0
        
        print("init.sql is OUTDATED. Run: python generate_init_sql.py")

        return 1

    INIT_SQL.write_text(expected, encoding="utf-8", newline="\n")
    print(f"init.sql written ({len(expected.splitlines())} lines).")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())