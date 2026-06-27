from sqlmodel import Session, select
from app.models import User, AuditLog
from app.services.auth import verify_password
from app.schemas.user import UserPublic, UserCreate
import uuid
from fastapi import HTTPException
from app.services.auth import get_password_hash
from app.enums import UserRoles


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).first()


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact your administrator.",
        )
    return user


def get_all_users(db: Session, offset: int = 0, limit: int = 100) -> list[User]:
    return list(db.exec(select(User).offset(offset).limit(limit)).all())


def create_user(db: Session, data: UserCreate, current_user: User):
    try:
        existing = db.exec(select(User).where(User.username == data.username)).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"User with username {data.username} already exists.",
            )
        # Prevent non-owners from creating Owner accounts
        if (
            data.role == UserRoles.OWNER
            and current_user.role != UserRoles.OWNER
            and not current_user.is_superAdmin
        ):
            raise HTTPException(
                status_code=403, detail="You don't have permission to assign this role."
            )

        # Prevent non-owners from creating superAdmin accounts
        if data.is_superAdmin and not current_user.is_superAdmin:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to create a superuser account.",
            )
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            role=data.role,
            is_active=data.is_active,
            is_superAdmin=data.is_superAdmin,
            hashed_password=get_password_hash(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        audit = AuditLog(
            action=f"Created user named {user.first_name} {user.last_name}",
            user_id=current_user.id,
        )
        db.add(audit)
        db.commit()

        return user
    except Exception:
        db.rollback()
        raise
