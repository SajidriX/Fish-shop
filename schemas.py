from pydantic import BaseModel, Field
from typing import Annotated

class User(BaseModel):
    username: str
    balance: float = 0
    password: str

class Fish(BaseModel):
    name: str
    price: float
    cathced: str

class UserGet(BaseModel):
    username: str
    balance: float

class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=4, max_length=35)]