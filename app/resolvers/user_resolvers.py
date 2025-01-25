from fastapi import HTTPException, Response, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.packages.schemas.user_schema import UserCreate, UserLogin
from app.packages.repositories.user.repository import create_user, get_user
from app.packages.repositories.user.utils import hash_password, verify_password, create_access_token, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def register(user: UserCreate, response: Response):
    try:
        existing_user = await get_user(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.password = hash_password(user.password)
        new_user = await create_user(user)
        
        access_token = create_access_token(data={"sub": user.username})
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # Temporarily set to False, will be True after the server runs on HTTPS
            samesite="lax"
        )
        
        return {"username": new_user["username"], "id": new_user["_id"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def login(user: UserLogin, response: Response):
    try:
        db_user = await get_user(user.username)
        if not db_user or not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.username})
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # Temporarily set to False, will be True after the server runs on HTTPS
            samesite="lax"
        )
        return {"username": db_user["username"], "id": db_user["_id"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def logout(response: Response):
    try:
        response.delete_cookie(key="access_token")
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
