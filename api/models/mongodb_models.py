from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from schemas.mongodb.mongodb_inventory import PyObjectId

# Pydantic database models to define how data is stored in MongoDB


class LocationMongo(BaseModel):
    id: Optional[str]  # ObjectId uses string
    name: str
    address: str
    state: str = None
    zip_code: int = None
    capacity: int

    class Config:
        # Maps to the 'id' field in the response
        json_encoders = {ObjectId: str}


class InventoryMongo(BaseModel):
    id: Optional[str]  # ObjectId uses string
    name: str
    location_id: str
    quantity: int
    description: str
    price: float
    width: float
    prescription_avail: bool
    tinted: bool
    polarized: bool
    anti_glare: bool
    user_id: int

    # Tells pydantic to use strings when serializing ObjectId
    class Config:
        json_encoders = {ObjectId: str}
