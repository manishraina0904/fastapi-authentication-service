from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.database.session import SessionLocal

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.blacklist_token import BlacklistToken

from app.schemas.user_schema import UserCreate

from app.utils.security import hash_password, verify_password, create_refresh_token
from app.utils.token import create_access_token

from app.utils.deps import get_current_user


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ---------------- DB ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- REGISTER ---------------- #

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        return {"error": "Email already registered"}

    hashed = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}


# ---------------- LOGIN ---------------- #

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:
        return {"error": "User not found"}

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        return {"error": "Wrong password"}

    access_token = create_access_token(
        {"sub": db_user.email}
    )

    refresh_token = create_refresh_token()

    db_token = RefreshToken(
        user_id=db_user.id,
        token=refresh_token
    )

    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ---------------- PROTECTED ---------------- #

@router.get("/protected")
def protected(
    user = Depends(get_current_user)
):

    return {
        "message": "Access OK",
        "user": user
    }


# ---------------- LOGOUT ---------------- #

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    black = db.query(BlacklistToken).filter(
        BlacklistToken.token == token
    ).first()

    if black:
        return {"message": "Already logged out"}

    new_black = BlacklistToken(
        token=token
    )

    db.add(new_black)
    db.commit()

    return {"message": "Logged out"}