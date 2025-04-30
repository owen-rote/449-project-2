from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Pydantic schemas for sending/recieving MongoDB data


from pydantic import BaseModel
from bson import ObjectId
from schemas.mongodb.mongodb_inventory import PyObjectId


class LocationCreate(BaseModel):
    name: str
    address: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: int = Field(..., ge=10000, le=99999)
    capacity: int = Field(..., ge=0)


class LocationRead(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    address: str
    state: str
    zip_code: int
    capacity: int

    class Config:
        # Config for handling ObjectID
        validate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[int] = Field(None, ge=10000, le=99999)
    capacity: Optional[int] = Field(None, ge=0)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
