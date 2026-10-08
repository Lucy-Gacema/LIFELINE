from sqlalchemy.orm import Session

from lifeline.models.expense import Expense
from lifeline.schemas.expenses import ExpenseCreate


def create_expense(db: Session, data: ExpenseCreate, user) -> Expense:
    expense = Expense(**data.model_dump(), created_by=user.user_id if user else None)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
