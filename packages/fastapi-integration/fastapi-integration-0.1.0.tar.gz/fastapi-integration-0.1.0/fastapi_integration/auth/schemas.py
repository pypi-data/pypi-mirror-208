from typing import Optional
import re


from pydantic import BaseModel, validator, EmailStr


class AuthModel(BaseModel):
    token_type: str
    access_token: str


class UserOut(BaseModel):
    id: int
    username: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def password_strength(cls, value):
        if len(value) < 8:
            raise ValueError(
                'Password should be at least 8 characters long'
            )
        elif (
            re.search(r'[a-z]', value) is None
        ) or (
            re.search(r'[A-Z]', value) is None
        ) or (
            re.search(r'[!@#$%^&*(),.?":{}|<>]', value) is None
        ):
            text = "Password should contain at least one uppercase letter"
            text += ", one lowercase letter, and one special character"
            raise ValueError(
                text
            )
        elif re.search(r'password', value, re.IGNORECASE) is not None:
            raise ValueError(
                'Password should not be a common password'
            )
        return value
