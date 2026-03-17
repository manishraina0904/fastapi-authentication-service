from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.session import Base


class BlacklistToken(Base):

    __tablename__ = "blacklist_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, index=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )