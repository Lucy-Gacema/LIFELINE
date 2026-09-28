from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.schemas.settings import BusinessSettingsUpdate, BusinessSettingsOut
from lifeline.services import settings_service

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.get("/", response_model=BusinessSettingsOut)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return settings_service.get_settings(db)


@router.patch("/", response_model=BusinessSettingsOut)
def update_settings(data: BusinessSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("change_settings"))):
    return settings_service.update_settings(db, data.model_dump(exclude_unset=True))
