from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category

def export():
    db = SessionLocal()
    articles = db.query(Article).all()
    
    print("\n" + "="*50)
    print("ZKOPÍRUJ VŠE POD TÍMTO ŘÁDKEM A POŠLI MI TO:")
    print("="*50 + "\n")
    
    print("articles_data = [")
    for a in articles:
        # Získání názvu kategorie (pokud existuje)
        cat_name = a.category.name if a.category else "Nezařazeno"
        
        print("    {")
        print(f"        'title': {repr(a.title)},")
        print(f"        'perex': {repr(a.perex)},")
        print(f"        'content': {repr(a.content)},")
        print(f"        'image_url': '{a.image_url}',")
        print(f"        'home_position': {a.home_position},")
        print(f"        'category_name': '{cat_name}',")
        print("    },")
    print("]")
    print("\n" + "="*50)

if __name__ == "__main__":
    export()