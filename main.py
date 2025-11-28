from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers import home
from app.core.database import engine
from app import models

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zpravodajský portál")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(home.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
