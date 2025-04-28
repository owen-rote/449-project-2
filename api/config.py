from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Universal variables for consistency =========================================
SECRET_KEY = "TODO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MYSQL_DATABASE_URL = "mysql+mysqlconnector://gvuser:1234@localhost/glassview"
MONGO_DATABASE_URL = "mongodb://localhost:27017"
MONGO_DB_NAME = "glassview-db"

# MySQL Connection ============================================================
engine = create_engine(MYSQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function for db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MongoDB Connection ==========================================================
mongo_client = MongoClient(MONGO_DATABASE_URL)
mongo_db = mongo_client[MONGO_DB_NAME]
