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
        allow_population_by_field_name = True
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
