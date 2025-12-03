import os
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.enums import Role, ArticleStatus
import app.models # Načte všechny modely

def reset_database():
    print("🧨 Mazání staré databáze...")
    # Smazání souboru (pokud existuje)
    if os.path.exists("news.db"):
        os.remove("news.db")
    
    print("🏗️  Vytváření nových tabulek...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("👤 Vytváření uživatelů...")
    admin = User(email="admin@zpravy.cz", name="Hlavní Admin", password_hash=hash_password("tajneheslo123"), role=Role.ADMIN, is_active=True)
    sef = User(email="sef@zpravy.cz", name="Karel Šéf", password_hash=hash_password("sef123"), role=Role.CHIEF_EDITOR, is_active=True)
    redaktor = User(email="jan.novak@zpravy.cz", name="Jan Novák", password_hash=hash_password("redaktor123"), role=Role.EDITOR, is_active=True)
    ctenar = User(email="pepa@mail.cz", name="Pepa Zdepa", password_hash=hash_password("pepa123"), role=Role.READER, is_active=True)
    
    db.add_all([admin, sef, redaktor, ctenar])
    db.commit()
    
    print("📂 Vytváření kategorií...")
    c_domaci = Category(name="Domácí", description="Zprávy z ČR")
    c_zahranici = Category(name="Zahraničí", description="Svět")
    c_sport = Category(name="Sport", description="Sport")
    c_tech = Category(name="Technologie", description="IT a Věda")
    c_eko = Category(name="Ekonomika", description="Byznys")
    
    db.add_all([c_domaci, c_zahranici, c_sport, c_tech, c_eko])
    db.commit()
    
    print("📰 Vytváření článků...")
    now = datetime.now(timezone.utc)
    
    # 1. Hlavní zpráva (Real Madrid)
    a1 = Article(
        title="Finále Ligy mistrů: Real Madrid vítězí",
        perex="Dramatické finále rozhodl gól v nastavení. Podívejte se na sestřih nejlepších momentů utkání.",
        content="<p>Dlouhý text článku...</p>",
        image_url="https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1000",
        status=ArticleStatus.PUBLISHED,
        home_position=1, # HLAVNÍ
        author_id=redaktor.id,
        category_id=c_sport.id,
        created_at=now
    )
    
    # 2. Vlevo (Metro)
    a2 = Article(
        title="Nová linka metra D se otevírá",
        perex="Pražané se konečně dočkali. Dlouho očekávaná linka metra D zahajuje provoz.",
        content="<p>Text článku...</p>",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Praha_metro_A_Nemocnice_Motol_platform_1.jpg/800px-Praha_metro_A_Nemocnice_Motol_platform_1.jpg",
        status=ArticleStatus.PUBLISHED,
        home_position=2, # VLEVO
        author_id=redaktor.id,
        category_id=c_domaci.id,
        created_at=now - timedelta(hours=1)
    )
    
    # 3. Střed (AI)
    a3 = Article(
        title="Průlom v umělé inteligenci",
        perex="Vědci představili nový model AI, který dokáže předpovídat počasí s přesností na minuty.",
        content="<p>Text...</p>",
        image_url="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1000",
        status=ArticleStatus.PUBLISHED,
        home_position=3, # STŘED
        author_id=redaktor.id,
        category_id=c_tech.id,
        created_at=now - timedelta(hours=2)
    )
    
    # 4. Vpravo (Máslo)
    a4 = Article(
        title="Ceny másla v Česku opět rostou",
        perex="Ekonomové varují před dalším zdražováním základních potravin před Vánoci.",
        content="<p>Text...</p>",
        image_url="https://images.unsplash.com/photo-1594026362947-8a66f272a71d?q=80&w=1000",
        status=ArticleStatus.PUBLISHED,
        home_position=4, # VPRAVO
        author_id=redaktor.id,
        category_id=c_eko.id,
        created_at=now - timedelta(hours=3)
    )
    
    # Ostatní do seznamu
    titles = [
        ("Zemětřesení v Japonsku nezpůsobilo škody", c_zahranici, "https://images.unsplash.com/photo-1586790924009-3242fb59c03b?q=80&w=1000"),
        ("Tesla svolává tisíce vozů", c_tech, "https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=1000"),
        ("Čeští hokejisté zahájili přípravu", c_sport, "https://images.unsplash.com/photo-1515703407324-5f7536b90aa8?q=80&w=1000"),
        ("Inflace klesá, hypotéky by mohly zlevnit", c_eko, "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?q=80&w=1000"),
        ("Nový iPhone překvapil výdrží", c_tech, "https://images.unsplash.com/photo-1512054502232-10a0a035d672?q=80&w=1000"),
        ("Slavia v derby rozdrtila Spartu", c_sport, "https://images.unsplash.com/photo-1522778119026-d647f0565c6a?q=80&w=1000")
    ]
    
    articles = [a1, a2, a3, a4]
    
    for i, (title, cat, img) in enumerate(titles):
        art = Article(
            title=title,
            perex="Lorem ipsum dolor sit amet...",
            content="<p>Obsah...</p>",
            image_url=img,
            status=ArticleStatus.PUBLISHED,
            home_position=0,
            author_id=redaktor.id,
            category_id=cat.id,
            created_at=now - timedelta(hours=4+i)
        )
        articles.append(art)
        
    db.add_all(articles)
    db.commit()
    
    print("✅ HOTOVO! Databáze je kompletně obnovena.")
    db.close()

if __name__ == "__main__":
    reset_database()