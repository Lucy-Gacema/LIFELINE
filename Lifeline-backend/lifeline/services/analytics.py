from sqlalchemy.orm import Session
from lifeline.repositories.analytics import analytics_repository
from lifeline.schemas.analytics import BusinessSummaryResponse

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = analytics_repository

    def get_financial_summary(self) -> BusinessSummaryResponse:
        money_tied_in_debts = self.repository.get_money_tied_in_debts(self.db)
        total_profit = self.repository.get_total_profit(self.db)
        total_revenue = self.repository.get_total_revenue(self.db)

        actual_pocket_cash_flow = total_revenue - money_tied_in_debts

        return BusinessSummaryResponse(
            total_profit=total_profit,
            money_tied_in_debts=money_tied_in_debts,
            actual_pocket_cash_flow=actual_pocket_cash_flow
        )
