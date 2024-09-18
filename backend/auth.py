from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status, HTTPException, Depends
from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from helper import authenticate_user, get_user_by_email
from schemas import Token
from pymongo.database import Database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "619609ac4686435b77197313ab6c4618daa8e6cc0f609018043ef7cbc98e236d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def access_token_for_login(db: Database, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> str:
    user = await authenticate_user(db, form_data.email, form_data.password)

    if not user:
        raise HTTPException(status=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email and password")

    access_token = create_access_token(
        {"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return access_token


async def decode_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WwW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(email)

    if not user:
        raise credentials_exception

    return user
