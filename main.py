from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers import home, auth, admin, comments
from app.core.database import engine, Base
import app.models 

# Vytvoření tabulek (pokud neexistují)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zpravodajský portál")

# Statické soubory (CSS, obrázky)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrace routerů (cest)
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)