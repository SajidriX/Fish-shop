from fastapi import APIRouter, Depends, HTTPException, Body, Path, Request, Header
from models import Fishes, init_db, Session
from schemas import Fish
from typing import List, Annotated
from fastapi.security import OAuth2PasswordBearer
from users.main_users import secret_key
from jose.jwt import decode
from jose.exceptions import JWTError

scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")


async def get_current_user(token: str = Depends(scheme)):
    try:
        
        payload = decode(token, secret_key, algorithms=["HS512"])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Неверный токен: пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id 
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

router = APIRouter()

@router.get("/fishes", response_model=List[Fish], tags=["Рыба"], summary="Получить всю рыбу")
async def get_fishes(db: Session = Depends(init_db),current_user_id: str = Depends(get_current_user)):
    return db.query(Fishes).all()

@router.post("/fish_sell", response_model=Fish, tags=["Рыба"], summary="Выставить рыбу на продажу")
async def sell_fish(
    request: Request,
    fish_data: Annotated[Fish, Body()],
    db: Session = Depends(init_db),
    current_user_id: str = Depends(get_current_user)
):
    csrf_token = request.cookies.get("csrf_access_token")
    if not csrf_token:
        raise HTTPException(status_code=400, detail="CSRF токен не найден в cookies")

    fish = Fishes(name=fish_data.name, price=fish_data.price, cathced=fish_data.cathced)
    db.add(fish)
    db.commit()
    db.refresh(fish)
    return fish

@router.delete("/fishes/{fish_id}", tags=["Рыба"], summary="Удалить рыбу")
async def delete_fish(fish_id: Annotated[int, Path(ge=0, le=100000)], db: Session = Depends(init_db),current_user_id: str = Depends(get_current_user)):
    fish = db.query(Fishes).filter(Fishes.id == fish_id).first()
    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")
    db.delete(fish)
    db.commit()
    return {"status": "Fish deleted"}

@router.patch("/fishes/{fish_id}", tags=["Рыба"], summary="Изменить рыбу")
async def update_fish(
    fish_id: Annotated[int, Path(ge=0, le=100000)],
    fish_data: dict = Body(...),
    db: Session = Depends(init_db),
    current_user_id: str = Depends(get_current_user)
    
):
    fish = db.query(Fishes).filter(Fishes.id == fish_id).first()
    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")
    
    for field, value in fish_data.items():
        setattr(fish, field, value)
    
    db.commit()
    return fish

@router.get("/fishes/place/{cathced}", response_model=List[Fish], tags=["Рыба"], summary="Фильтрация рыбы по месту выловки")
async def get_fish_by_place(cathced: Annotated[str, Path(min_length=3, max_length=20)], db: Session = Depends(init_db),current_user_id: str = Depends(get_current_user)):
    return db.query(Fishes).filter(Fishes.cathced == cathced).all()

@router.get("/fishes/byName/{name}", response_model=List[Fish], tags=["Рыба"], summary="Фильтрация рыбы по названию")
async def get_fish_by_name(name: Annotated[str, Path(min_length=2, max_length=55)], db: Session = Depends(init_db),current_user_id: str = Depends(get_current_user)):
    return db.query(Fishes).filter(Fishes.name == name).all()