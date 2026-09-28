from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from lifeline.models.user import User
from lifeline.schemas.assistant import AssistantMessageIn, AssistantMessageOut
from lifeline.services import ai_agent

router = APIRouter(prefix="/api/v1/assistant", tags=["Business Assistant"])


@router.post("/message", response_model=AssistantMessageOut)
def send_message(data: AssistantMessageIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    return ai_agent.process_message(db, current_user, data)


@router.get("/daily-briefing")
def daily_briefing(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    from lifeline.services import report_service
    snapshot = report_service.get_business_health_snapshot(db)
    insights = []

    if snapshot["low_stock_products"]:
        names = ", ".join(p["name"] for p in snapshot["low_stock_products"][:3])
        insights.append(f"Low stock: {names}.")
    if snapshot["outstanding_customer_credit"] > 0:
        insights.append(f"Customers owe KSh {snapshot['outstanding_customer_credit']:.0f} in total.")
    if snapshot["supplier_balances_owed"] > 0:
        insights.append(f"You owe suppliers KSh {snapshot['supplier_balances_owed']:.0f}.")
    if snapshot["top_products_today"]:
        insights.append(f"Best seller so far today: {snapshot['top_products_today'][0]['name']}.")

    return {"greeting": "Good morning. Here's your business briefing.", "insights": insights[:5], "snapshot": snapshot}
