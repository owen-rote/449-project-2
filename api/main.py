from fastapi import FastAPI
from routers import inventory

app = FastAPI(
    title="GlassView"
)

app.include_router(inventory.router, prefix="/inventory", tags=['inventory'])

@app.get("/")
def root():
    return {"message": "GlassView API"}