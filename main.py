from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers import home, auth, admin, comments, favorites
# ZMĚNA: Import z nového umístění
from app.models.db import engine, Base
from app.core.filters import format_date
import app.models 

# Vytvoření tabulek (pokud neexistují)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zpravodajský portál")

# --- REGISTRACE FILTRU PRO DATUM ---
# Musíme filtr přidat do všech routerů, které používají šablony
routers_with_templates = [home, admin, comments, favorites]

for router_module in routers_with_templates:
    if hasattr(router_module, "templates"):
        router_module.templates.env.filters["format_date"] = format_date
# ------------------------------------

# Statické soubory (CSS, obrázky)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrace routerů (cest)
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)
app.include_router(favorites.router)