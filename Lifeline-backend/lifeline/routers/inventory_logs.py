from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.orm import joinedload
from lifeline.models import InventoryLogs
from uuid import UUID
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException
from database import get_db
from lifeline.services.inventory_logs import InventoryLogService
from lifeline.schemas.inventory_logs import InventoryLogCreate, InventoryLogUpdate, InventoryLogResponse

router = APIRouter(prefix="/inventory_logs", tags=["Inventory Logs"])

def get_srv(db: Session = Depends(get_db)) -> InventoryLogService:
    return InventoryLogService(db)

@router.post("/", response_model=InventoryLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    payload: InventoryLogCreate, 
    s: InventoryLogService = Depends(get_srv), 
    db: Session = Depends(get_db)
):
    try:
        new_log = s.create_log(payload.model_dump())
        complete_log = (
            db.query(InventoryLogs)
            .options(joinedload(InventoryLogs.product))
            .filter(InventoryLogs.inventory_logs_id == new_log.inventory_logs_id)
            .first()
        )
        
        return complete_log
    
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[InventoryLogResponse], status_code=status.HTTP_200_OK)
def read_logs(s: InventoryLogService = Depends(get_srv)):
    return s.get_all_logs()

@router.get("/{log_id}", response_model=InventoryLogResponse, status_code=status.HTTP_200_OK)
def read_log(log_id: UUID, s: InventoryLogService = Depends(get_srv)):
    try:
        return s.get_log(log_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{log_id}", response_model=InventoryLogResponse, status_code=status.HTTP_200_OK)
def update_log(log_id: UUID, p: InventoryLogUpdate, s: InventoryLogService = Depends(get_srv)):
    try:
        return s.update_log(log_id, p.model_dump(exclude_unset=True, mode="json"))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
