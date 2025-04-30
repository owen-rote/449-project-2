from pydantic import BaseModel, Field
from typing import Optional

# Pydantic schemas for sending/recieving MySQL data


# LocationCreate is identical and reusable from schemas.mongodb


class LocationRead(BaseModel):
    location_id: int
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
