from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class OrderCreate(BaseModel):
    product: str = Field(min_length=1)
    side: Literal["BUY", "SELL"]
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


class OrderResponse(BaseModel):
    order_id: str
    product: str
    side: str
    quantity: int
    price: float
    status: str

    model_config = ConfigDict(from_attributes=True)