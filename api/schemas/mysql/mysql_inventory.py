from pydantic import BaseModel, Field
from typing import Optional

# Pydantic schemas for sending/recieving MySQL data


class InventoryCreate(BaseModel):
    name: str
    location_id: int  # Location validation is done in the endpoint
    quantity: int = Field(..., ge=0)
    description: str
    price: float = Field(..., ge=0)
    width: float = Field(..., ge=0)
    prescription_avail: bool
    tinted: bool
    polarized: bool
    anti_glare: bool


class InventoryRead(BaseModel):
    id: int
    name: str
    location_id: int
    quantity: int
    description: str
    price: float
    width: float
    prescription_avail: bool
    tinted: bool
    polarized: bool
    anti_glare: bool

    # Makes fastAPI auto-convert sqlalchemy models to schemas
    class Config:
        orm_mode = True


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    location_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    prescription_avail: Optional[bool] = None
    tinted: Optional[bool] = None
    polarized: Optional[bool] = None
    anti_glare: Optional[bool] = None
