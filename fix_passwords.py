"""
Script to update existing user passwords with proper bcrypt hashing.
Run this after setting up the new security module to ensure
existing users (admin, jan.novak) can log in.
"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def fix_passwords():
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            # Re-hash the password (assuming stored passwords are plain text or old hash)
            # For demo purposes, we use known passwords
            known_passwords = {
                "admin@zpravy.cz": "admin123",
                "jan.novak@email.cz": "heslo123",
            }
            
            if user.email in known_passwords:
                new_hash = hash_password(known_passwords[user.email])
                user.password_hash = new_hash
                print(f"Updated password for user: {user.email}")
            else:
                print(f"Unknown user, skipping: {user.email}")
        
        db.commit()
        print("Password update complete.")
        
    finally:
        db.close()


if __name__ == "__main__":
    fix_passwords()
