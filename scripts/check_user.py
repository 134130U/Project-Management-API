from app.db.database import SessionLocal
from app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test@test.com").first()
        if user:
            print(f"User test@test.com found with id {user.id}")
        else:
            print("User test@test.com NOT found")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
