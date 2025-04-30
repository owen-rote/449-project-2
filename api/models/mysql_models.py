from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from config import engine
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy models to define how data is stored in MySQL

Base = declarative_base()


class LocationMySQL(Base):
    __tablename__ = "location"

    location_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)


class InventoryMySQL(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    # Link to location
    location_id = Column(Integer, ForeignKey("location.location_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    prescription_avail = Column(Boolean, nullable=False)
    tinted = Column(Boolean, nullable=False)
    polarized = Column(Boolean, nullable=False)
    anti_glare = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)


class UserMySql(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # 'user' or 'admin'
