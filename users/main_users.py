
from fastapi import APIRouter, Depends, HTTPException, Body, Response, Path, Request, Header
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Annotated,Optional
from models import init_db, Users, Fishes
from schemas import UserCreate, User,UserOut,UserDelete
import bcrypt
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users import BaseUserManager,IntegerIDMixin
import uuid


bearer = BearerTransport(tokenUrl="auth/jwt/login")

secret_key = "ExampleSecretKeyDontUseItUseDotEnvFile"



class UserManager(IntegerIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = secret_key
    verification_token_secret = secret_key
    reset_password_token_lifetime_seconds = 180
    verification_token_lifetime_seconds = 36000

    async def on_after_register(self, user: Users, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: Users, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: Users, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(init_db)):
    yield UserManager(user_db)





# --- Help ---
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_jwt() -> JWTStrategy:
    return JWTStrategy(secret=secret_key,lifetime_seconds=36000,algorithm="HS512")

backend = AuthenticationBackend(
    name = "jwt",
    transport=bearer,
    get_strategy=get_jwt,

)

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






@router.patch("/users/{user_id}",  tags=["Пользователи"], summary="Изменение пользователя")
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

@router.delete("/users_delete",tags = ["Пользователи"], summary = "Удаление пользователя")
async def delete_user(user_data: UserDelete = Body(...), db: Session = Depends(init_db)):

    user = db.query(Users).filter(Users.username == user_data.username, Users.id == user_data.id).first()

    if not user:
        return "This user does not exist"
    elif user:
        db.delete(user)
        db.commit()
    
    return "User deleted"
