from fastapi import HTTPException, status
from app.packages.schemas.user_schema import UserCreate, UserLogin
from app.packages.repositories.user.repository import create_user, get_user
from app.packages.repositories.user.utils import hash_password, verify_password, create_access_token

async def register(user: UserCreate):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    user.password = hash_password(user.password)
    new_user = await create_user(user)
    return new_user

async def login(user: UserLogin):
    db_user = await get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": db_user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
