from fastapi import FastAPI, Depends

from app.database.session import engine, Base

from app.modules.auth.router import router as auth_router

from app.utils.deps import get_current_user

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.blacklist_token import BlacklistToken


app = FastAPI()


# create tables
Base.metadata.create_all(bind=engine)


# routers
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Backend working"}


@app.get("/profile")
def profile(user=Depends(get_current_user)):

    return {
        "message": "Protected route",
        "user": user
    }