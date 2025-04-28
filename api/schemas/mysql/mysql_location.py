from pydantic import BaseModel, Field
from typing import Optional

# Pydantic schemas for sending/recieving MySQL data


class LocationCreate(BaseModel):
    name: str
    address: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: int = Field(..., ge=10000, le=99999)
    capacity: int = Field(..., ge=0)


class LocationRead(BaseModel):
    id: int
    name: str
    address: str
    state: str
    zip_code: int
    capacity: int

    class Config:
        from_attributes = True


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[int] = Field(None, ge=10000, le=99999)
    capacity: Optional[int] = Field(None, ge=0)
