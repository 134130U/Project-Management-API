from jose import jwt, JWTError
from app.config import settings
from app.core.exceptions import UnauthorizedException
from app.schemas.auth import TokenData

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=["HS256"]
        )
        email: str = payload.get("email")
        if email is None:
            raise UnauthorizedException()
        return TokenData(email=email)
    except JWTError:
        raise UnauthorizedException()
