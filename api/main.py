from fastapi import FastAPI
from config import engine
from models.mysql_models import Base
from routers import inventory, auth, location

app = FastAPI(title="GlassView")

# Generate the tables of the db automatically
Base.metadata.create_all(bind=engine)

app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "GlassView API"}
