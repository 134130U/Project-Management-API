from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.auth import decode_token
from app.core.exceptions import UnauthorizedException, NotFoundException

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token_data = decode_token(token.credentials)
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise UnauthorizedException(detail="User not found")
    return user