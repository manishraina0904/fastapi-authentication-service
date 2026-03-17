from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.refresh_token import RefreshToken
from app.utils.token import create_access_token


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    clean_token = refresh_token.replace('"', '')

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == clean_token
    ).first()

    if not db_token:
        return {"error": "Invalid refresh token"}

    new_access = create_access_token(
        {"sub": db_token.user_id}
    )

    return {
        "access_token": new_access,
        "token_type": "bearer"
    }