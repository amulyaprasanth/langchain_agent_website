from pydantic import BaseModel


class User(BaseModel):
    fullname: str | None = None
    email: str
    disabled: bool | None = None
    
    
class UserInDB(User):
    hashed_password: str 
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginSchema(BaseModel):
    email: str
    password: str
    
    
class RegisterFormSchema(BaseModel):
    firstname: str
    lastname: str | None = None
    email: str
    password: str
    confirmPassword: str