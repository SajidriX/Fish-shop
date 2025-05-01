from fastapi import APIRouter, Depends, HTTPException, Body, Response, Path
from contextlib import asynccontextmanager
from models import Base, engine, init_db, Session, SessionLocal, Users
from  schemas import User, UserGet, UserCreate
from typing import List, Annotated, Dict
from authx import AuthX, AuthXConfig
from models import Fishes
import bcrypt

config = AuthXConfig()
config.JWT_ALGORITHM = "HS512"
config.JWT_SECRET_KEY = "12201222Sajison1222!11QQqq!!T95E42012Artur"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt) 
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

router = APIRouter()

@router.post("/users_create", response_model=User, tags=["Пользователи"], summary="Создание пользователя") 
async def create_user(user_data: Annotated[UserCreate, Body()], db: Session = Depends(init_db)):
    hashed_password = hash_password(user_data.password)
    user = Users(username=user_data.username, password = hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user) 
    return user


@router.get("/users", response_model=List[UserGet], tags=["Пользователи"], summary="Получение всех пользователей")
async def get_users(db: Session = Depends(init_db)):
    try:
        users = db.query(Users).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении пользователей: {str(e)}"
        )

@router.delete("/users/{user_id}",  dependencies=[Depends(security.access_token_required)],tags=["Пользователи"], summary="Удаление пользователя")
async def delete_user(user_id: Annotated[int, Path(ge=1, le=1000000)], db: Session = Depends(init_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "User deleted"}

@router.patch("/users/{user_id}",  dependencies=[Depends(security.access_token_required)],tags=["Пользователи"], summary="Изменение пользователя")
async def update_user(
    user_id: Annotated[int, Path(ge=1, le=1000000)],
    user_data: Annotated[Dict, Body(...)],
    db: Session = Depends(init_db)
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.commit()
    return user

@router.post("/login", tags=["Пользователи"], summary="логин")
async def login_user(
    user_data: Annotated[UserCreate, Body()],  
    response: Response, 
    db: Session = Depends(init_db)
):
    db_user = db.query(Users).filter(Users.username == user_data.username).first()
    
    if not db_user or not verify_password(user_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    token = security.create_access_token(uid=db_user.username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}

@router.get("/protected", dependencies=[Depends(security.access_token_required)], tags=["Пользователи"], summary="Роут работает только если у пользователя есть jwt")
async def protected_route(db: Session = Depends(init_db)):
    fishes = db.query(Fishes).all()
    return {"You have loginned! Congratulations! There are all our fishes for example": fishes}

@router.delete("/logout", tags=["Пользователи"], summary="Выход из аккаунта")
async def logout_user(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "You have logged out"}