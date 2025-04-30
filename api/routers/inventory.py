from fastapi import APIRouter, FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from schemas.mysql import mysql_inventory
from schemas.mongodb import mongodb_inventory

from models.mysql_models import InventoryMySQL
from models.mongodb_models import InventoryMongo

from routers.auth import get_current_user, get_admin_user
from config import get_db

router = APIRouter(prefix="/inventory")

# Post inventory entry


# Get all inventory entries
@router.get("/", response_model=List[mysql_inventory.InventoryRead])
def get_all_inventory(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return db.query(InventoryMySQL).all()


# Get inventory at location_id

# Get inventory by inventory_id

# Edit inventory at certain location

# Delete inventory at certain location
