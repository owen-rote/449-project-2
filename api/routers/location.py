from bson import ObjectId
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
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
    mongo_doc = location.dict()
    mongo_collection.insert_one(mongo_doc)

    return {"mysql_id": mysql_location.location_id, "mongodb": "inserted"}


# Get all locations from MongoDB
@router.get("/mongodb", response_model=List[mongodb_location.LocationRead])
def get_all_locations_mongo(
    mongo_collection: Collection = Depends(get_mongo_location_collection),
):
    locations = mongo_collection.find()  # Find all locations
    return locations

# Get all locations from MySQL
@router.get("/mysql", response_model=List[mysql_location.LocationRead])
def get_all_locations_mysql(db: Session = Depends(get_db)):
    all_locations = db.query(LocationMySQL).all()  # Get all records from LocationMySQL
    return all_locations  # This will be automatically serialized by Pydantic


@router.get("/mongodb/{location_id}", response_model=mongodb_location.LocationRead)
def get_location_by_ID_mongo(
    location_id: str,
    mongo: Collection = Depends(get_mongo_location_collection)
):
    
    try:
        obj = mongo.find_one({"_id": ObjectId(location_id)})
    except:
        raise HTTPException(status_code=404, detail="Not found")
    if obj != None:
        return obj
    raise HTTPException(status_code=404,detail="Not Found")

# Get location by ID from MySQL DB
@router.get("/mysql/{location_id}", response_model=mysql_location.LocationRead)
def get_location_by_ID_mysql(location_id: int, db: Session = Depends(get_db)):
    location = db.query(LocationMySQL).filter_by(location_id=location_id).first()
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )
    
    return location


# Edit a location
@router.put("/mongodb/{location_id}", response_model=mongodb_location.LocationRead)
def post_location_mongo(
    location_id: str,
    location_item: mongodb_location.LocationUpdate,
    mongo: Collection = Depends(get_mongo_location_collection),
    current_user=Depends(get_admin_user)
):  
    try :
        item = mongo.find_one({'_id': ObjectId(location_id)})
    except:
        raise HTTPException(status_code=404,detail="Location not found")
    if not item:
        raise HTTPException(status_code=404,detail="Location not found")
    if not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")
    
    for key, value in location_item.model_dump().items():
        item[key] = value
    #try:

        mongo.update_one({'_id': ObjectId(location_id)}, {'$set':item})
    #except :
    #    raise HTTPException(status_code=400, detail="Invalid Form")
    return item


@router.put("/mysql/{location_id}", response_model=mysql_location.LocationRead)
def update_location(
    location_id: int,
    location_item: mysql_location.LocationUpdate,
    db: Session = Depends(get_db),
    current_user: UserMySql = Depends(get_admin_user)
):
    location = db.query(LocationMySQL).filter_by(location_id=location_id).first()
    if not location:
        raise HTTPException(
            status_code=404, 
            detail="Location not found"
        )
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
        )
    
    for key, value in location_item.model_dump().items():
        setattr(location, key, value)

    try:
        db.commit()
        db.refresh(location)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid Form"
        )
    return location

# # Delete a location
@router.delete("/mongodb/{location_id}", response_model=Dict[str,str])
def delete_location_mongo(
    location_id: str,
    mongo: Collection = Depends(get_mongo_location_collection),
    current_user=Depends(get_admin_user)
):  
    try :
        item = mongo.find_one({'_id': ObjectId(location_id)})
    except:
        raise HTTPException(status_code=404,detail="Location not found")
    if not item:
        raise HTTPException(status_code=404,detail="Location not found")
    if not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")

    try:
        mongo.delete_one({'_id': ObjectId(location_id)})
    except :
        raise HTTPException(status_code=400, detail="Invalid Form")
    return {"message":"deleted successfully"}

@router.delete("/mysql/{location_id}", response_model=Dict[str, str])
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: UserMySql = Depends(get_admin_user)
):
    location = db.query(LocationMySQL).filter_by(location_id=location_id).first()
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
            )

    if not current_user.role == "admin":
        raise HTTPException(
            status_code=401, 
            detail="Not Authorized"
        )
     
    try:
        db.delete(location)
        db.commit()
    except:
        raise HTTPException(
            status_code=400, 
            detail="Invalid form"
        )
    return {"message": "Location sucessfully deleted"}