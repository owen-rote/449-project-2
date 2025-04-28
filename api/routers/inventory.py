from fastapi import APIRouter, FastAPI, HTTPException, Depends
from schemas.mongodb import mongodb_inventory
from schemas.mysql import mysql_inventory

router = APIRouter(prefix="/auth")

# Get all inventory entries

# Get inventory at location_id

# Get inventory by inventory_id

# Edit inventory at certain location

# Delete inventory at certain location
