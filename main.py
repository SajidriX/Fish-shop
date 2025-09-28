from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine, init_db as get_db,Users
from users.main_users import router as users_router,backend,get_user_manager
from fishes.main_fishes import router as fishes_router
from wall.main_wall import router as wall_router
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
from collections import defaultdict
from fastapi_users import FastAPIUsers
from schemas import UserCreate,UserGet,UserDelete,UserOut,User


fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [backend]
)

# Lifespan для управления жизненным циклом БД
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Создаем таблицы при старте
    print("🟢 Создаем таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Здесь работает приложение
    yield
    
    # 3. Закрываем соединения при завершении
    print("🔴 Закрываем соединение с БД...")
    engine.dispose()

origins = [
    "http://127.0.0.1:8000",  # Основной домен API
    "http://localhost:8000",   # Альтернативный адрес
    "http://localhost:3000",   # Для фронтенда (React/Vue)
    "http://127.0.0.1:3000",   # Альтернативный адрес фронтенда
]

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(users_router)
app.include_router(fishes_router)
app.include_router(wall_router)
app.include_router(
    fastapi_users.get_auth_router(backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserGet, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserGet),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserGet, User),
    prefix="/users",
    tags=["users"],
)



request_history = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host  
    current_time = time.time()
    

    request_history[client_ip] = [
        timestamp for timestamp in request_history[client_ip] 
        if current_time - timestamp < 5
    ]
    
    
    if len(request_history[client_ip]) >= 8:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    
    
    request_history[client_ip].append(current_time)
    
    
    response = await call_next(request)
    return response


if __name__ == "__main__":
    uvicorn.run(app=app,port=2012,reload=False)
