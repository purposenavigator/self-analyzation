from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
