from uuid import UUID
from app.models import UserBase
from pydantic import BaseModel

class UserPublic(UserBase):
    id: UUID
    
class UserCreate(UserBase):
    password: str
    
class UserUpdate(UserBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    
class TokenData(BaseModel):
    username: str | None = None
    
class UserLogin(BaseModel):
    username: str | None = None
    hashed_password: str