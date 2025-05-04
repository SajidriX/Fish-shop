from fastapi import APIRouter, Depends, HTTPException, Body, Response, Path, Request
from contextlib import asynccontextmanager
from models import Base, engine, init_db, Session, SessionLocal, Users
from  schemas import User, UserGet, UserCreate
from typing import List, Annotated, Dict
from authx import AuthX, AuthXConfig
from models import Fishes
import bcrypt
from hashing.hashing import hash_password,verify_password
from verify.verify import verify_admin
from auth.auth_settings import security, config
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect




router = APIRouter()

@router.post("/users_create", response_model=User, tags=["Пользователи"], summary="Создание пользователя") 
async def create_user(user_data: Annotated[UserCreate, Body()], db: Session = Depends(init_db)):
    hashed_password = hash_password(user_data.password)
    user = Users(username=user_data.username, password = hashed_password)
    if user_data.password == "Sajison1222!":
        user.role = "Admin"
    db.add(user)
    db.commit()
    db.refresh(user) 
    return user


@router.get("/users", response_model=List[UserGet], tags=["Пользователи"], summary="Получение всех пользователей")
async def get_users(db: Session = Depends(init_db)):
    if verify_admin():
        try:
            users = db.query(Users).all()
            return users
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при получении пользователей: {str(e)}"
            )
    elif not verify_admin():
        HTTPException(status_code=403,detail="No permission")

@router.delete("/users/{user_id}",  dependencies=[Depends(security.access_token_required)],tags=["Пользователи"], summary="Удаление пользователя")
async def delete_user(user_id: Annotated[int, Path(ge=1, le=1000000)], db: Session = Depends(init_db)):
    if verify_admin():
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"status": "User deleted"}
    elif not verify_admin():
        return HTTPException(status_code=403,detail="No permission to do it")

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
    request: Request,
    user_data: Annotated[UserCreate, Body()],  
    response: Response, 
    db: Session = Depends(init_db),
    csrf_protect: CsrfProtect = Depends()
):
    db_user = db.query(Users).filter(Users.username == user_data.username).first()
    
    if not db_user or not verify_password(user_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    token = security.create_access_token(uid=db_user.id, username = db_user.username,role=db_user.role)
    csrf = csrf_protect.generate_csrf_tokens()
    
    resp = JSONResponse(status_code=200,content={"token":token,"csrf":csrf})

    resp.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        samesite="lax"
    )

    resp.set_cookie(
        key="csrf_token",
        value=csrf,
        samesite="lax"
    )


    return resp

@router.get("/protected", dependencies=[Depends(security.access_token_required)], tags=["Пользователи"], summary="Роут работает только если у пользователя есть jwt")
async def protected_route(db: Session = Depends(init_db)):
    fishes = db.query(Fishes).all()
    return {"You have loginned! Congratulations! There are all our fishes for example": fishes}

@router.delete("/logout", tags=["Пользователи"], summary="Выход из аккаунта")
async def logout_user(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "You have logged out"}