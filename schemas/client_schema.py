from datetime import datetime, time
from decimal import Decimal

from pydantic import ConfigDict, Field

from schemas.base_schema import BaseSchema

class ClientBase(BaseSchema):
    name: str = Field(min_length=3, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)
    monthly_income: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    usual_city: str = Field(min_length=2, max_length=80)
    usual_start_time: time
    usual_end_time: time

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    active: bool

class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime