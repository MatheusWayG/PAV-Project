from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class RuleBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    weight: int = Field(ge=1, le=100)
    threshold: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    window_minutes: int | None = Field(default=None, gt=0)

class RuleCreate(RuleBase):
    code: str = Field(min_length=2, max_length=50, pattern=r"^[A-Z][A-Z0-9_]*$")

class RuleUpdate(RuleBase):
    active: bool

class RuleOut(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    active: bool