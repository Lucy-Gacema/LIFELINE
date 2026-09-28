from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.models.expense import Expense
from lifeline.schemas.expenses import ExpenseCreate, ExpenseOut
from lifeline.services import expense_service

router = APIRouter(prefix="/api/v1/expenses", tags=["Expenses"])


@router.get("/", response_model=list[ExpenseOut])
def list_expenses(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_expenses"))):
    return db.query(Expense).order_by(Expense.date.desc()).limit(200).all()


@router.post("/", response_model=ExpenseOut, status_code=201)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_expenses"))):
    return expense_service.create_expense(db, data, current_user)
