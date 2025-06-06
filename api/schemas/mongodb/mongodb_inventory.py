from pydantic import BaseModel, Field, field_validator
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from typing import Optional
from bson import ObjectId

# Pydantic schemas for sending/recieving MongoDB data

class PyObjectId(ObjectId):
    # Custom types to handle ObjectID in MongoDB
    # This allows Pydantic to correctly serialize it as a string
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetJsonSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, **kwargs):
        # Return a schema indicating that this type should be a string
        return {
            "type": "string"
        }
    
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


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

    @field_validator('id', mode='before')
    def validate_id(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        return v

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
