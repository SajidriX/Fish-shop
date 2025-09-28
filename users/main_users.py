from fastapi import APIRouter, Depends, HTTPException, Body, Response, Path, Request, Header
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Annotated
from models import init_db, Users, Fishes
from schemas import UserCreate, User,UserOut
import bcrypt



# --- Help ---
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


router = APIRouter()

# --- PATCH update user ---
@router.patch("/users/{user_id}", tags=["Пользователи"], summary="Изменение пользователя")
async def update_user(
    user_id: Annotated[int, Path(ge=1, le=1000000)],
    user_data: Annotated[Dict, Body(...)],
    db: Session = Depends(init_db),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user





# --- POST create user ---
@router.post("/users_create", response_model=UserOut, tags=["Пользователи"], summary="Создание пользователя")
async def create_user(user_data: UserCreate = Body(...), db: Session = Depends(init_db)):
    hashed_password = hash_password(user_data.password)


    user = Users(
        username=user_data.username,
        password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user