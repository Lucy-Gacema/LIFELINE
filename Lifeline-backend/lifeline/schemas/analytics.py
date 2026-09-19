from pydantic import BaseModel
from decimal import Decimal

class BusinessSummaryResponse(BaseModel):
    total_profit: Decimal
    money_tied_in_debts: Decimal
    actual_pocket_cash_flow: Decimal
