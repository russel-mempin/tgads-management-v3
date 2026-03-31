from typing import Annotated, cast
from fastapi import Depends, HTTPException, status
from app.database import get_session
from app.services.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from app.crud.user import get_user_by_username
import jwt
from sqlmodel import Session
from app.schemas.user import TokenData
from jwt.exceptions import InvalidTokenError
from app.models import User



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],  db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[cast(str, ALGORITHM)])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return role_checker