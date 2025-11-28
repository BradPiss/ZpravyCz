from app.core.database import SessionLocal
from app.models.article import Article

def fix_metro_image():
    db = SessionLocal()
    
    # Najdeme článek s metrem
    article = db.query(Article).filter(Article.title.like("%zlevnit%")).first()
    
    if article:
        print(f"Měním obrázek u článku: {article.title}")
        # Vkládáme ten tvůj dlouhý odkaz ze Seznamu
        article.image_url = "https://d15-a.sdn.cz/d_15/c_img_F_E/OosBqcL.jpeg?fl=cro,0,0,800,450|res,1280,,1|webp,75"
        db.commit()
        print("✅ Hotovo! Obrázek je změněný.")
    else:
        print("❌ Článek o metru nebyl nalezen.")
    
    db.close()

if __name__ == "__main__":
    fix_metro_image()