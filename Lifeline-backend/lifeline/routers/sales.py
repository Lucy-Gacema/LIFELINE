from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException
from database import get_db
from lifeline.services.sales import SaleService
from lifeline.schemas.sales import SaleCreate, SaleUpdate, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])

def get_srv(db: Session = Depends(get_db)) -> SaleService:
    return SaleService(db)

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(p: SaleCreate, s: SaleService = Depends(get_srv)):
    try:
        return s.create_sale(p.model_dump(mode="json"))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[SaleResponse], status_code=status.HTTP_200_OK)
def read_sales(s: SaleService = Depends(get_srv)):
    return s.get_all_sales()

@router.get("/{sale_id}", response_model=SaleResponse, status_code=status.HTTP_200_OK)
def read_sale(sale_id: UUID, s: SaleService = Depends(get_srv)):
    try:
        return s.get_sale(sale_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{sale_id}", response_model=SaleResponse, status_code=status.HTTP_200_OK)
def update_sale(sale_id: UUID, p: SaleUpdate, s: SaleService = Depends(get_srv)):
    try:
        return s.update_sale(sale_id, p.model_dump(exclude_unset=True, mode="json"))
    except (EntityNotFoundException, DatabaseOperationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
