from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import security
from app.core.config import settings
from app.db.database import get_db
from app.db import models
from app.schemas import schemas

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", scheme_name="email")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint that accepts email and password.
    
    Parameters:
    - email: User's email address
    - password: User's password
    
    Returns:
    - access_token: JWT token for authentication
    - token_type: Type of token (always "bearer")
    """
    print(f"Login attempt with email: {login_data.email}")
    
    # Ищем пользователя только по email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        print("Login failed: incorrect credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Login successful for user: {user.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Received registration request for user: {user.username}, email: {user.email}")
    
    # Проверяем только уникальность email
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    
    if db_user_email:
        print(f"Email {user.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    print("Creating new user...")
    hashed_password = security.get_password_hash(user.password)
    print(f"Password hashed successfully: {hashed_password[:10]}...")
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    print("User model created")
    
    db.add(db_user)
    print("User added to session")
    
    try:
        db.commit()
        print("User committed to database")
    except Exception as e:
        print(f"Error committing to database: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user in database"
        )
    
    db.refresh(db_user)
    print("User refreshed from database")
    
    print("Generating access token...")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": db_user.email},  # Используем email вместо username
        expires_delta=access_token_expires
    )
    print("Access token generated successfully")
    
    print("User created successfully")
    return {"access_token": access_token, "token_type": "bearer"} 