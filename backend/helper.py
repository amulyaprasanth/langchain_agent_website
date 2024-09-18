from passlib.context import CryptContext
from fastapi import HTTPException, status
from schemas import User, UserInDB
from pymongo.database import Database

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pass(password: str):
    return pass_context.hash(password)


def verify_pass(plain_password: str, hash_password: str):
    return pass_context.verify(plain_password, hash_password)


async def get_user_by_email(email: str) -> User:
    user_dict = users_collection.find_one(
        {"email": email}, {"_id": False})

    if not user_dict:
        raise HTTPException(
            status_code=400, detail="Could find user in the database")

    return User(**user_dict)


async def authenticate_user(db: Database, email: str, password: str)-> UserInDB:
    user_dict = db['login'].find_one(
        {"email": email}, {"_id": False})

    user = UserInDB(**user_dict)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Incorrect username or password")

    if verify_pass(password, user.hashed_password):
        return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Incorrect username or password")
