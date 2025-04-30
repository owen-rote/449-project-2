from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Pydantic schemas for sending/recieving MongoDB data

class PyObjectId(ObjectId):
    # Custom types to handle ObjectID in MongoDB
    # This allows Pydantic to correctly serialize it as a string
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, **kwargs):
        # Return a schema indicating that this type should be a string
        return {
            "type": "string",
        }


class InventoryCreate(BaseModel):
    name: str
    location_id: int  # Validate location separately
    quantity: int = Field(..., ge=0)
    description: str
    price: float = Field(..., ge=0)
    width: float = Field(..., ge=0)
    prescription_avail: bool
    tinted: bool
    polarized: bool
    anti_glare: bool


class InventoryRead(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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

    class Config:
        # Config for handling ObjectID
        validate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


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

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
