from datetime import datetime

from pydantic import ConfigDict, Field

from schemas.base_schema import BaseSchema

class AlertBase(BaseSchema):
    reason: str = Field(min_length=3, max_length=500)

class AlertCreate(AlertBase):
    transaction_id: int = Field(gt=0)
    rule_id: int = Field(gt=0)
    points: int = Field(gt=0, le=100)

class AlertUpdate(AlertBase):
    pass

class AlertOut(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    rule_id: int
    rule_code: str
    points: int
    created_at: datetime