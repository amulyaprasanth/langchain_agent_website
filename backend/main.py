from fastapi import FastAPI, Depends, status, HTTPException, Response
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserInDB, Token, RegisterFormSchema, LoginSchema
from pymongo import MongoClient
from helper import hash_pass, verify_pass
from auth import access_token_for_login, decode_token, oauth2_scheme

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def connect_db():
    client = MongoClient("mongodb://localhost:27017")

    app.database = client["test"]
    print("Connected to the DB")


@app.on_event("shutdown")
async def disconnect_db():
    client.close()

    print("Disconnected from database")


@app.post("/register_user")
async def register_user(form_data: RegisterFormSchema):
    fullname = form_data.firstname + " " + \
        form_data.lastname  # Added space between names
    email = form_data.email
    password = form_data.password

    hashed_password = await hash_pass(password)  # Await the hash_pass function

    user = get_user(email)

    if not user:
        users_collection.insert_one({
            "fullname": fullname,
            "email": email,
            "hashed_password": hashed_password,
            "disabled": False  # Fixed 'disabled' typo
        })

        return Response(status_code=status.HTTP_201_CREATED)

    else:
        return Response(status_code=status.HTTP_409_CONFLICT)


@app.post("/token")
async def login(response: Response, form_data: LoginSchema):
    token = await access_token_for_login(app.database, form_data)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    return {"message", "Login successful"}


@app.get("/users/me")
async def read_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await decode_token(token)
    return user
