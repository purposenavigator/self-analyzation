from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
