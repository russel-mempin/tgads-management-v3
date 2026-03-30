from sqlmodel import Session, select
from app.models import User
from app.services.auth import verify_password


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).first()

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user