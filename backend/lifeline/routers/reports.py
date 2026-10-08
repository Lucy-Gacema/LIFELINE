from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.services import report_service

router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Dashboard"])


@router.get("/sales-summary")
def sales_summary(
    period: str = "today",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("access_reports")),
):
    return report_service.get_sales_summary(db, period)


@router.get("/profit-summary")
def profit_summary(
    period: str = "today",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_profit")),
):
    return report_service.get_profit_summary(db, period)


@router.get("/top-products")
def top_products(
    period: str = "today",
    by: str = "quantity",
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("access_reports")),
):
    return report_service.get_top_products(db, period, limit=limit, by=by)


@router.get("/slow-moving")
def slow_moving(
    days: int = 14,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("access_reports")),
):
    return report_service.get_slow_moving_products(db, days)


@router.get("/expenses-summary")
def expenses_summary(
    period: str = "today",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("access_reports")),
):
    return report_service.get_expense_summary(db, period)


@router.get("/business-health")
def business_health(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):

    return report_service.get_business_health_snapshot(db)
