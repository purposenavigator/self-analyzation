from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from app.packages.database import users_collection
from app.packages.repositories.user.repository import get_user
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM")

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from the database
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user["username"], "id": user["_id"]}
