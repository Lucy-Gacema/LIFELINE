from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from lifeline.services.users import UserService
from lifeline.schemas.users import UserCreate, UserUpdate, UserResponse
from lifeline.schemas.users import UserLoginRequest, TokenResponse
from lifeline.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])

def get_srv(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(p: UserCreate, s: UserService = Depends(get_srv)):
    return s.register_user(p)

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def read_all_users(s: UserService = Depends(get_srv)):
    return s.get_all_users()

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def read_user(user_id: UUID, s: UserService = Depends(get_srv)):
    return s.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: UUID, p: UserUpdate, s: UserService = Depends(get_srv)):
    return s.update_user(user_id, p.model_dump(exclude_unset=True))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, s: UserService = Depends(get_srv)):
    s.delete_user(user_id)
    return None

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_user(credentials: UserLoginRequest,s : UserService=Depends(get_srv)):
    
    return s.authenticate_user(credentials)
