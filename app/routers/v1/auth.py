from fastapi import APIRouter, HTTPException, Depends, Request, Header
from passlib.context import CryptContext
from pydantic import BaseModel
import shortuuid
from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from datetime import datetime, timedelta, timezone
import os

import database as db


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN"))

# setup router
router = APIRouter()

# setup password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define request models
class UserCredentials(BaseModel):
    email: str
    password: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =================== ENDPOINTS =============================
@router.post("/register")
def register_user(user_credentials: UserCredentials):
    user_id = shortuuid.uuid()
    hashed_password = hash_password(user_credentials.password)
    user_id = db.create_user(user_id, user_credentials.email, hashed_password)

    # automatically login user on registraction
    login_response = login_user(user_credentials=user_credentials)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User was not registered.")
    else:
        return {"message": "User registered and logged in",
                "user_id": login_response["user_id"],
                "user_email": login_response["user_email"],
                "access_token": login_response["access_token"]
                }


@router.post("/login")
def login_user(user_credentials: UserCredentials):
    result = db.get_user_by_email(user_credentials.email)
    print("result: ", result)
    if result is None or not verify_password(user_credentials.password, result[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        access_token = create_access_token(result[0])
        print(f"access token: {access_token}")
    return {"message": "Login successful",
            "user_id": result[0],
            "user_email": user_credentials.email,
            "access_token": access_token
            }


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRES_IN)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        # Try to convert to int if possible, otherwise keep as string
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            # If it's not an integer, just return the string value
            pass
        return user_id
    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]
    return verify_token(token) 


@router.get("/secure-data")
def secure_endpoint(user_id: int = Depends(get_current_user)):
    return {"message": "You are authorized", "user_id": user_id}