from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    is_active: bool
    is_admin: bool

    class ConfigDict:
        orm_mode = True
