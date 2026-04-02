from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import Login, Token
from app.schemas.user import UserCreate
from app.core.security import hash_password, create_token, verify_password
from app.api.deps import get_db
from app.models.user import User
from app.core.exceptions import BadRequestException

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    email = user_in.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise BadRequestException(detail="Email already registered")
    
    user = User(email=email, password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    token = create_token({"email": email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(login_in: Login, db: Session = Depends(get_db)):
    email = login_in.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(login_in.password, user.password):
        raise BadRequestException(detail="Incorrect email or password")
    
    token = create_token({"email": user.email})
    return {"access_token": token, "token_type": "bearer"}