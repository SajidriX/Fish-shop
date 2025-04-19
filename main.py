from fastapi import FastAPI, Query, Body, Path, Header, Cookie, File, UploadFile, Depends, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine, init_db as get_db
from users.main_users import router as users_router
from fishes.main_fishes import router as fishes_router
from fastapi.staticfiles import StaticFiles
import uvicorn


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


if __name__ == "__main__":
    uvicorn.run(app=app)