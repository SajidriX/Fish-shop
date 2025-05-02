from fastapi import APIRouter, Depends, HTTPException, Body, Path
from contextlib import asynccontextmanager
from models import Base, engine, init_db, Session, SessionLocal, Fishes
from  schemas import Fish
from typing import List, Annotated
from users.main_users import security


router = APIRouter()

@router.get("/fishes", response_model=List[Fish], tags=["Рыба"], summary="Получить всю рыбу",  dependencies=[Depends(security.access_token_required)])
async def get_fishes(db: Session = Depends(init_db)):
    fishes = db.query(Fishes).all()
    return fishes

@router.post("/fish_sell", response_model=Fish, tags=["Рыба"], summary="Выставить рыбу на продажу",  dependencies=[Depends(security.access_token_required)])
async def sell_fish(fish_data: Annotated[Fish, Body()], db: Session = Depends(init_db)):
    fish = Fishes(name=fish_data.name, price=fish_data.price, cathced=fish_data.cathced)
    db.add(fish)
    db.commit()
    db.refresh(fish)
    return fish

@router.delete("/fishes/{fish_id}", tags=["Рыба"], summary="Удалить рыбу",  dependencies=[Depends(security.access_token_required)])
async def delete_fish(fish_id: Annotated[int, Path(ge=0,le=100000)], db: Session = Depends(init_db)):
    fish = db.query(Fishes).filter(Fishes.id == fish_id).first()
    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")
    db.delete(fish)
    db.commit()
    return {"status": "Fish deleted"}

@router.patch("/fishes/{fish_id}", tags=["Рыба"], summary="Изменить рыбу",  dependencies=[Depends(security.access_token_required)])
async def update_fish(
    fish_id: Annotated[int, Path(ge=0,le=100000)],
    fish_data: dict = Body(...),
    db: Session = Depends(init_db)
):
    fish = db.query(Fishes).filter(Fishes.id == fish_id).first()
    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")
    
    for field, value in fish_data.items():
        setattr(fish, field, value)
    
    db.commit()
    return fish

@router.get("/fishes/place/{cathced}",response_model=List[Fish],tags=["Рыба"],summary="Фильтрация рыбы по месту выловки",  dependencies=[Depends(security.access_token_required)])
async def get_fish_by_place(
    cathced: Annotated[str,Path(min_length=3,max_length=20)],
    db: Session = Depends(init_db)
):
    fish = db.query(Fishes).filter(Fishes.cathced== cathced).all()
    return fish
    
@router.get("/fishes/byName/{name}",response_model=List[Fish], tags=["Рыба"], summary="Фильтрация рыбы по названию",  dependencies=[Depends(security.access_token_required)])
async def get_fish_by_name(
        name: Annotated[str,Path(min_length=2,max_length=55)],
        db: Session = Depends(init_db)
):
    fishes = db.query(Fishes).filter(Fishes.name == name).all()
    return fishes