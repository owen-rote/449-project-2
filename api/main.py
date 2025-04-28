from fastapi import FastAPI
from routers import inventory, auth, location

app = FastAPI(title="GlassView")

app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "GlassView API"}
