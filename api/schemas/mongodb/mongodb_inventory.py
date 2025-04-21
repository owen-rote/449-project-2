from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


# Custom types to handle ObjectID in MongoDB
# This allows Pydantic to correctly serialize it as a string
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        # Make sure the ObjectID is valid
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


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
        allow_population_by_field_name = True
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
