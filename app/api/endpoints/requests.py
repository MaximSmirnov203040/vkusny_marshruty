from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.api.endpoints.auth import get_current_user
from app.bot.notifications import send_group_notification
import asyncio

router = APIRouter()

@router.post("/guest", response_model=schemas.TravelRequest)
async def create_guest_request(
    request: schemas.GuestTravelRequestCreate,
    db: Session = Depends(get_db)
):
    # Проверяем существование тура
    tour = db.query(models.Tour).filter(models.Tour.id == request.tour_id).first()
    if tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    # Проверяем доступность мест
    if tour.available_spots <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available spots for this tour"
        )
    
    # Создаем заявку
    db_request = models.TravelRequest(
        tour_id=request.tour_id,
        status="pending",
        guest_name=request.guest_name,
        guest_email=request.guest_email,
        guest_phone=request.guest_phone,
        comment=request.comment
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Отправляем уведомление
    asyncio.create_task(send_group_notification(db_request))
    
    return db_request

@router.post("/", response_model=schemas.TravelRequest)
async def create_request(
    request: schemas.TravelRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Проверяем существование тура
    tour = db.query(models.Tour).filter(models.Tour.id == request.tour_id).first()
    if tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    # Проверяем доступность мест
    if tour.available_spots <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available spots for this tour"
        )
    
    # Создаем заявку
    db_request = models.TravelRequest(
        user_id=current_user.id,
        tour_id=request.tour_id,
        status="pending"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Отправляем уведомление
    asyncio.create_task(send_group_notification(db_request))
    
    return db_request

@router.get("/my", response_model=List[schemas.TravelRequest])
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    requests = db.query(models.TravelRequest).filter(
        models.TravelRequest.user_id == current_user.id
    ).all()
    return requests

@router.get("/", response_model=List[schemas.TravelRequest])
def get_all_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    requests = db.query(models.TravelRequest).all()
    return requests

@router.put("/{request_id}/status", response_model=schemas.TravelRequest)
def update_request_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_request = db.query(models.TravelRequest).filter(
        models.TravelRequest.id == request_id
    ).first()
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if status not in ["pending", "approved", "rejected", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    db_request.status = status
    if status == "approved":
        # Уменьшаем количество доступных мест
        tour = db_request.tour
        if tour.available_spots > 0:
            tour.available_spots -= 1
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available spots for this tour"
            )
    
    db.commit()
    
    # Отправляем уведомление
    asyncio.create_task(send_group_notification(db_request))
    
    return db_request 