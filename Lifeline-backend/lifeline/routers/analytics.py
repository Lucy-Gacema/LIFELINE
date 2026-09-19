from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db

from lifeline.schemas.analytics import BusinessSummaryResponse
from lifeline.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Business Analytics"])

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/summary", response_model=BusinessSummaryResponse, status_code=status.HTTP_200_OK)
def read_business_summary(s: AnalyticsService = Depends(get_analytics_service)):

    return s.get_financial_summary()
