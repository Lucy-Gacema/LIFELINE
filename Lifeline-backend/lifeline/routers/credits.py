from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from lifeline.services.credits import CreditService
from lifeline.schemas.credits import CreditCreate, CreditUpdate, CreditResponse
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException

router = APIRouter(prefix="/credits", tags=["Credits"])

def get_credit_service(db: Session = Depends(get_db)) -> CreditService:
    return CreditService(db)

@router.get("/", response_model=List[CreditResponse], status_code=status.HTTP_200_OK)
def read_all_credits(
    s: CreditService = Depends(get_credit_service),
    db: Session = Depends(get_db) 
): 
    return s.get_all_credit(db=db)

@router.post("/", response_model=CreditResponse, status_code=status.HTTP_201_CREATED)
def create_credit(p: CreditCreate, s: CreditService = Depends(get_credit_service)): 
    try:
        return s.create_credit(p.model_dump())
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{credit_id}", response_model=CreditResponse, status_code=status.HTTP_200_OK)
def read_credit(
    credit_id: UUID, 
    s: CreditService = Depends(get_credit_service),
    db: Session = Depends(get_db) 
):
    try:
        return s.get(db=db, id=credit_id) 
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.put("/{credit_id}", response_model=CreditResponse, status_code=status.HTTP_200_OK)
def update_credit(credit_id: UUID, p: CreditUpdate, s: CreditService = Depends(get_credit_service)): 
    try:
        return s.update_credit(credit_id, p.model_dump(exclude_unset=True))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credit(credit_id: UUID, s: CreditService = Depends(get_credit_service)): 
    try:
        s.delete_credit(credit_id)
        return None
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

