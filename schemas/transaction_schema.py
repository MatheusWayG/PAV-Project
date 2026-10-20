from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from entities.transaction import Classification, TransactionType

class TransactionBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

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
    risk_score: int
    classification: Classification
    created_at: datetime