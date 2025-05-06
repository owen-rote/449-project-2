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
from bson import ObjectId

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
        copy["user_id"] = current_user.user_id

        mongo.insert_one(copy.copy())
        mongo_item = mongo.find_one(copy.copy())
    
        sql_inventory = InventoryMySQL(**copy)
        db.add(sql_inventory)
        db.commit()
        db.refresh(sql_inventory)
    except :
        raise HTTPException(status_code=400, detail="Invalid Form")



    return {'mongo':mongo_item, 'mysql':sql_inventory}

# Get all inventory entries
@router.get("/mysql", response_model=List[mysql_inventory.InventoryRead])
def get_all_inventory_sql(
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        return db.query(InventoryMySQL).all()
    else:
        return db.query(InventoryMySQL).filter(
            InventoryMySQL.user_id == current_user.user_id
            )

@router.get("/mongodb", response_model=List[mongodb_inventory.InventoryRead])
def get_all_inventory_mongo(
    mongo: Collection = Depends(get_mongo_inventory_collection), current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        return mongo.find()
    else:
        return mongo.find(
            {"user_id": current_user.user_id})

# Get inventory at location_id
@router.get("/mysql/by_location/{location_id}", response_model=List[mysql_inventory.InventoryRead])
def get_inventory_by_location_sql(
    location_id: int,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        return db.query(InventoryMySQL).filter(InventoryMySQL.location_id == location_id).all()
    else:
        return db.query(InventoryMySQL).filter(
            InventoryMySQL.location_id == location_id,
            InventoryMySQL.user_id == current_user.user_id).all()
    
@router.get("/mongodb/by_location/{location_id}", response_model=List[mongodb_inventory.InventoryRead])
def get_inventory_by_location_mongo(
    location_id: int,
    mongo: Collection = Depends(get_mongo_inventory_collection), current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        return mongo.find({"location_id": location_id})
    else:
        return mongo.find(
            {"location_id": location_id, "user_id": current_user.user_id})

# Get inventory by inventory_id
@router.get("/mysql/{inventory_id}", response_model=mysql_inventory.InventoryRead)
def get_inventory_sql(
    inventory_id: int,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    obj = None
    if(current_user.role == "admin"):
        obj = db.query(InventoryMySQL).filter(InventoryMySQL.inventory_id == inventory_id).first()
    else:
        obj = db.query(InventoryMySQL).filter(
            InventoryMySQL.inventory_id == inventory_id,
            InventoryMySQL.user_id == current_user.user_id).first()
    if obj == None:
        raise HTTPException(status_code=404, detail="Not found")
    return obj
    
@router.get("/mongodb/{inventory_id}", response_model=mongodb_inventory.InventoryRead)
def get_inventory_mongo(
    inventory_id: str,
    mongo: Collection = Depends(get_mongo_inventory_collection), current_user=Depends(get_current_user)
):
    if(current_user.role == "admin"):
        try:
            obj = mongo.find_one({"_id": ObjectId(inventory_id)})
        except:
            raise HTTPException(status_code=404, detail="Not found")
        if obj != None:
            return obj
    else:
        try:
            obj = mongo.find_one({
            "_id": ObjectId(inventory_id),
            "user_id": current_user.user_id})
        except:
            raise HTTPException(status_code=404, detail="Not found")
        if obj != None:
            return obj
    raise HTTPException(status_code=404,detail="Not Found")
    
# Edit inventory at certain location
@router.put("/mysql/{inventory_id}", response_model=mysql_inventory.InventoryRead)
def put_inventory_sql(
    inventory_id: int,
    inventory_item: mysql_inventory.InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    item = db.query(InventoryMySQL).get(inventory_id)
    if not item:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item.user_id == current_user.user_id and not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")

    for key, value in inventory_item.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
        db.refresh(item)
    except :
        raise HTTPException(status_code=400, detail="Invalid Form")
    return item

@router.put("/mongodb/{inventory_id}", response_model=mongodb_inventory.InventoryRead)
def put_inventory_mongo(
    inventory_id: str,
    inventory_item: mongodb_inventory.InventoryUpdate,
    mongo: Collection = Depends(get_mongo_inventory_collection),
    current_user=Depends(get_current_user)
):  
    try :
        item = mongo.find_one({'_id': ObjectId(inventory_id)})
    except:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item["user_id"] == current_user.user_id and not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")
    
    for key, value in inventory_item.model_dump().items():
        item[key] = value
    #try:

        mongo.update_one({'_id': ObjectId(inventory_id)}, {'$set':item})
    #except :
    #    raise HTTPException(status_code=400, detail="Invalid Form")
    return item
    
# Delete inventory at certain location
@router.delete("/mysql/{inventory_id}", response_model=Dict[str,str])
def delete_inventory_sql(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    item = db.query(InventoryMySQL).get(inventory_id)
    if not item:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item.user_id == current_user.user_id and not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")

    try:
        db.delete(item)
        db.commit()
    except :
        raise HTTPException(status_code=400, detail="Invalid Form")
    return {"message":"deleted successfully"}

@router.delete("/mongodb/{inventory_id}", response_model=Dict[str,str])
def delete_inventory_mongo(
    inventory_id: str,
    mongo: Collection = Depends(get_mongo_inventory_collection),
    current_user=Depends(get_current_user)
):  
    try :
        item = mongo.find_one({'_id': ObjectId(inventory_id)})
    except:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item:
        raise HTTPException(status_code=404,detail="Inventory not found")
    if not item["user_id"] == current_user.user_id and not current_user.role == "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")

    try:
        mongo.delete_one({'_id': ObjectId(inventory_id)})
    except :
        raise HTTPException(status_code=400, detail="Invalid Form")
    return {"message":"deleted successfully"}