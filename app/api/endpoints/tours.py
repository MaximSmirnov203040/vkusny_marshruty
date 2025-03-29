from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.api.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Tour])
def get_tours(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    tours = db.query(models.Tour).offset(skip).limit(limit).all()
    return tours

@router.get("/popular", response_model=List[schemas.Tour])
def get_popular_tours(
    limit: int = 6,
    db: Session = Depends(get_db)
):
    # Получаем туры, отсортированные по количеству заявок
    tours = db.query(models.Tour).order_by(models.Tour.available_spots.desc()).limit(limit).all()
    return tours

@router.get("/hot", response_model=List[schemas.Tour])
def get_hot_tours(
    db: Session = Depends(get_db)
):
    tours = db.query(models.Tour).filter(models.Tour.is_hot == True).all()
    return tours

@router.get("/{tour_id}", response_model=schemas.Tour)
def get_tour(
    tour_id: int,
    db: Session = Depends(get_db)
):
    tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
    if tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    return tour

@router.post("/", response_model=schemas.Tour)
def create_tour(
    tour: schemas.TourCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db_tour = models.Tour(**tour.dict())
    db.add(db_tour)
    db.commit()
    db.refresh(db_tour)
    return db_tour

@router.put("/{tour_id}", response_model=schemas.Tour)
def update_tour(
    tour_id: int,
    tour: schemas.TourCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db_tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
    if db_tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    for key, value in tour.dict().items():
        setattr(db_tour, key, value)
    db.commit()
    db.refresh(db_tour)
    return db_tour

@router.delete("/{tour_id}")
def delete_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db_tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
    if db_tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    db.delete(db_tour)
    db.commit()
    return {"message": "Tour deleted successfully"} 