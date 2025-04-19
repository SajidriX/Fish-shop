from fastapi import APIRouter, Depends, HTTPException, Body
from contextlib import asynccontextmanager
from models import Base, engine, init_db, Session, SessionLocal, Fishes
from  schemas import Fish
from typing import List
import users.main_users


router = APIRouter()

@router.get("/fishes", response_model=List[Fish])
async def get_fishes(db: Session = Depends(init_db)):
    fishes = db.query(Fishes).all()
    return fishes

@router.post("/fish_sell", response_model=Fish, dependencies=[Depends(users.main_users.security.access_token_required)])
async def sell_fish(fish_data: Fish, db: Session = Depends(init_db)):
    fish = Fishes(name=fish_data.name, price=fish_data.price, cathced=fish_data.cathced)
    db.add(fish)
    db.commit()
    db.refresh(fish)
    return fish

@router.delete("/fishes/{fish_id}", dependencies=[Depends(users.main_users.security.access_token_required)])
async def delete_fish(fish_id: int, db: Session = Depends(init_db)):
    fish = db.query(Fishes).filter(Fishes.id == fish_id).first()
    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")
    db.delete(fish)
    db.commit()
    return {"status": "Fish deleted"}

@router.patch("/fishes/{fish_id}", dependencies=[Depends(users.main_users.security.access_token_required)])
async def update_fish(
    fish_id: int,
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