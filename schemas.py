from pydantic import BaseModel, Field
from typing import Annotated,Optional,Literal

class User(BaseModel):
    username: str
    balance: float = 0
    password: str

class Fish(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=28)]
    price: Annotated[float, Field(ge=0,le=1000000)]
    cathced: Annotated[str, Field(min_length=3,max_length=50)]

class UserGet(BaseModel):
    username: str
    balance: float

class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=4, max_length=35)]


class UserOut(BaseModel):
    id:int
    username:str
    balance:int

    class Config:
        orm_mode=True