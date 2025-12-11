from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def fix():
    db = SessionLocal()
    print("🔐 Aktualizuji hesla na bcrypt...")
    
    users = {
        "admin@zpravy.cz": "tajneheslo123",
        "jan.novak@zpravy.cz": "redaktor123"
    }
    
    for email, pwd in users.items():
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = hash_password(pwd)
            print(f"✅ Heslo pro {email} aktualizováno.")
            
    db.commit()
    db.close()

if __name__ == "__main__":
    fix()