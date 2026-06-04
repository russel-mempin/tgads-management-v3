from sqlmodel import Session, select
from app.models import User, AuditLog
from app.services.auth import verify_password
from app.schemas.user import UserPublic, UserCreate
import uuid
from fastapi import HTTPException
from app.services.auth import get_password_hash


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).first()

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_all_users(db: Session, offset: int = 0, limit: int = 100) -> list[User]:
    return list(
        db.exec(
            select(User).offset(offset).limit(limit)
        ).all()
    )

def create_user(db: Session, data: UserCreate, current_user_id: uuid.UUID):
    try:
        existing = db.exec(
            select(User).where(User.username == data.username)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"User with username {data.username} already exists."
            )
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            role=data.role,
            is_active=data.is_active,
            is_superAdmin=data.is_superAdmin,
            hashed_password=get_password_hash(data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        audit = AuditLog(
            action=f"Created user named {user.first_name} {user.last_name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return user
    except Exception:
        db.rollback()
        raise