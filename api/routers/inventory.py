from fastapi import APIRouter, FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict

from schemas.mysql import mysql_inventory
from schemas.mongodb import mongodb_inventory

from models.mysql_models import InventoryMySQL
from models.mongodb_models import InventoryMongo
from pymongo.collection import Collection

from routers.auth import get_current_user, get_admin_user
from config import get_db, get_mongo_inventory_collection

router = APIRouter(prefix="/inventory")

# Post inventory entry
@router.post("/", response_model=Dict[str, mysql_inventory.InventoryRead | mongodb_inventory.InventoryRead])
def get_all_inventory(
    inventory_item: mysql_inventory.InventoryCreate,
    db: Session = Depends(get_db), mongo: Collection = Depends(get_mongo_inventory_collection),
    current_user=Depends(get_current_user)
):  
    copy = inventory_item.model_dump()
    try :
        mongo.insert_one(copy.copy())
        mongo_item = mongo.find_one(copy.copy())
    
        copy["user_id"] = current_user.user_id
        sql_inventory = InventoryMySQL(**copy)
        db.add(sql_inventory)
        db.commit()
        db.refresh(sql_inventory)
    except :
        return {"error": "Invalid Form"}, 400



    return {'mongo':mongo_item, 'mysql':sql_inventory}

# Get all inventory entries
@router.get("/", response_model=List[mysql_inventory.InventoryRead])
def get_all_inventory(
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    return db.query(InventoryMySQL).all()


# Get inventory at location_id
@router.get("/by_location/{location_id}", response_model=List[mysql_inventory.InventoryRead])
def get_inventory_by_location(
    location_id: int,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        return db.query(InventoryMySQL).filter(InventoryMySQL.location_id == location_id).all()
    else:
        return db.query(InventoryMySQL).filter(
            InventoryMySQL.location_id == location_id,
            InventoryMySQL.user_id == current_user.user_id).all()

# Get inventory by inventory_id

# Edit inventory at certain location

# Delete inventory at certain location
