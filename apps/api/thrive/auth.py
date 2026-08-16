from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

DEMO_EMAIL = "alex@thriveos.demo"


def current_user(
    x_user_id: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    user = (
        db.get(User, x_user_id)
        if x_user_id
        else db.scalar(select(User).where(User.email == DEMO_EMAIL))
    )
    if not user:
        raise HTTPException(status_code=401, detail="No active user. Seed the demo or register.")
    return user
