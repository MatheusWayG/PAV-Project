from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from schemas.base_schema import BaseSchema

from entities.transaction import Classification, TransactionType
from schemas.alert_schema import AlertOut

class TransactionBase(BaseSchema):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    transaction_type: TransactionType
    destination: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=80)
    occurred_at: datetime

class TransactionCreate(TransactionBase):
    client_id: int = Field(gt=0)

class TransactionUpdate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    # Calculated by the system, never sent by the client.
    risk_score: int
    classification: Classification
    created_at: datetime
    # Why the transaction received its score (one alert per rule that fired).
    alerts: list[AlertOut]