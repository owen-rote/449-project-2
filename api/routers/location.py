from fastapi import APIRouter, FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pymongo.collection import Collection

from schemas.mysql import mysql_location
from schemas.mongodb import mongodb_location

from models.mysql_models import LocationMySQL, UserMySql
from models.mongodb_models import LocationMongo

from routers.auth import get_current_user, get_admin_user
from config import get_db, get_mongo_location_collection

router = APIRouter(prefix="/location")


# Create new location
# This creates parallel entities in both Mongo and MySQL
@router.post("/")
def create_location(
    location: mongodb_location.LocationCreate,
    db: Session = Depends(get_db),
    mongo_collection: Collection = Depends(get_mongo_location_collection),
    current_user: UserMySql = Depends(get_admin_user),  # Ensure the user is an admin
):
    # Insert into MySQL
    mysql_location = LocationMySQL(**location.dict())
    db.add(mysql_location)
    db.commit()
    db.refresh(mysql_location)

    # Insert into MongoDB
    mongo_collection.insert_one(location.dict())

    return {"mysql_id": mysql_location.location_id, "mongodb": "inserted"}


# Get all locations from MongoDB
# @router.get("/mongodb", response_model=List[mongodb_location.LocationRead])
# def get_all_locations_mongo(
#     mongo_collection: Collection = Depends(get_mongo_location_collection),
# ):
#     locations = mongo_collection.find()  # Find all locations

#     # Convert cursor to list and return as response
#     return [mongodb_location.LocationRead(**location) for location in locations]


# Get all locations from MySQL
@router.get("/mysql", response_model=List[mysql_location.LocationRead])
def get_all_locations_mysql(db: Session = Depends(get_db)):
    all_locations = db.query(LocationMySQL).all()  # Get all records from LocationMySQL
    return all_locations  # This will be automatically serialized by Pydantic


# Get location by ID from MongoDB
# Get location by ID from MySQL DB


# Edit a location

# Delete a location
