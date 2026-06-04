from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.database import get_session
from app.schemas.user import Token, UserPublic, UserCreate
from app.crud.user import authenticate_user, get_all_users, create_user
from datetime import timedelta
from app.services.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.models import User
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", role=user.role, first_name=user.first_name, last_name=user.last_name)

@router.get("/", response_model=list[UserPublic])
def read_all_users(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_users(db, offset=offset, limit=limit)

@router.post("/", response_model=UserPublic)
def create(data: UserCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_user(db, data, current_user.id)