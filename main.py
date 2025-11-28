from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers import home, auth
from app.core.database import engine, Base
# Důležité: Tento import načte modely, aby o nich SQLAlchemy vědělo
import app.models 

# Vytvoření tabulek v databázi při startu
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zpravodajský portál")

# Mount static files (CSS, obrázky)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers (zde budeme přidávat další)
app.include_router(home.router)
app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}