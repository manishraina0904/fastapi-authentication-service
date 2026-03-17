from jose import jwt, JWTError

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.blacklist_token import BlacklistToken

from app.utils.token import SECRET_KEY, ALGORITHM



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ---------------- DB ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- CURRENT USER ---------------- #

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # ✅ Check blacklist first
    black = db.query(BlacklistToken).filter(
        BlacklistToken.token == token
    ).first()

    if black:
        raise HTTPException(
            status_code=401,
            detail="Token blacklisted"
        )

    # ✅ Decode JWT
    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return email

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )