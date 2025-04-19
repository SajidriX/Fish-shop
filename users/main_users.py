from fastapi import APIRouter, Depends, HTTPException, Body, Response
from contextlib import asynccontextmanager
from models import Base, engine, init_db, Session, SessionLocal, Users
from  schemas import User, UserGet
from typing import List
from authx import AuthX, AuthXConfig
from models import Fishes

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "12201222Sajison1222!"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


router = APIRouter()

@router.post("/users_create", response_model=User) 
async def create_user(user_data: User, db: Session = Depends(init_db)):
    user = Users(username=user_data.username, balance=user_data.balance, password = user_data.password)
    db.add(user)
    db.commit()
    db.refresh(user) 
    return user


@router.get("/users", response_model=List[UserGet])
async def get_users(db: Session = Depends(init_db)):
    try:
        users = db.query(Users).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении пользователей: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(init_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "User deleted"}

@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict = Body(...),
    db: Session = Depends(init_db)
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.commit()
    return user

@router.post("/login")
async def login_user(user: User,response: Response, db: Session = Depends(init_db)):
    query = db.query(Users).filter(Users.username == user.username, Users.password == user.password).first()
    if not query:
        raise HTTPException(status_code=404, detail="User not found")    
    
    token = security.create_access_token(uid=user.username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {"acces token": token}

@router.get("/protected", dependencies=[Depends(security.access_token_required)])
async def protected_route(db: Session = Depends(init_db)):
    fishes = db.query(Fishes).all()
    return {"You have loginned! Congratulations! There are all our fishes for example": fishes}